package com.atlasuse.pos;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/** One atomic state snapshot. No financial documents, customer records or device credentials. */
final class DraftStore extends SQLiteOpenHelper {
    static final class Draft {
        String id = UUID.randomUUID().toString();
        long created = System.currentTimeMillis();
        String mode = "takeaway", table = "", note = "";
        Cart cart = new Cart();
        Draft copy() {
            Draft result = new Draft();
            result.id = id; result.created = created; result.mode = mode;
            result.table = table; result.note = note; result.cart = cart.copy();
            return result;
        }
    }
    static final class State {
        Draft active = new Draft();
        final List<Draft> held = new ArrayList<>();
        boolean arabic;
    }
    DraftStore(Context context) { this(context, "atlas_preview_drafts.db"); }
    DraftStore(Context context, String databaseName) { super(context, databaseName, null, 1); }
    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE draft_state (id INTEGER PRIMARY KEY CHECK (id=1), payload TEXT NOT NULL)");
    }
    @Override public void onUpgrade(SQLiteDatabase db, int old, int next) {
        throw new IllegalStateException("Explicit draft migration required");
    }

    State load(Catalog catalog) throws Exception {
        try (Cursor cursor = getReadableDatabase().rawQuery("SELECT payload FROM draft_state WHERE id=1", null)) {
            if (!cursor.moveToFirst()) return new State();
            JSONObject root = new JSONObject(cursor.getString(0));
            if (root.getInt("schema") != 1 || !catalog.hash.equals(root.getString("catalog_hash")))
                throw new IllegalStateException("Draft catalog changed; explicit review required");
            State state = new State();
            state.active = readDraft(root.getJSONObject("active"), catalog);
            state.arabic = root.getBoolean("arabic");
            JSONArray held = root.getJSONArray("held");
            if (held.length() > 50) throw new IllegalStateException("Draft limit");
            for (int i = 0; i < held.length(); i++) state.held.add(readDraft(held.getJSONObject(i), catalog));
            return state;
        }
    }

    void save(State state, Catalog catalog) throws Exception {
        JSONObject root = new JSONObject();
        root.put("schema", 1); root.put("catalog_hash", catalog.hash);
        root.put("arabic", state.arabic); root.put("active", writeDraft(state.active));
        JSONArray held = new JSONArray();
        for (Draft draft : state.held) held.put(writeDraft(draft));
        root.put("held", held);
        ContentValues values = new ContentValues();
        values.put("id", 1); values.put("payload", root.toString());
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            if (db.insertWithOnConflict("draft_state", null, values, SQLiteDatabase.CONFLICT_REPLACE) == -1)
                throw new IllegalStateException("Draft write failed");
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }

    private JSONObject writeDraft(Draft draft) throws Exception {
        JSONObject row = new JSONObject();
        row.put("id", draft.id); row.put("created", draft.created); row.put("mode", draft.mode);
        row.put("table", draft.table); row.put("note", draft.note);
        JSONArray lines = new JSONArray();
        for (Cart.Line line : draft.cart.lines()) {
            JSONObject value = new JSONObject();
            value.put("code", line.item.code); value.put("quantity", line.quantity());
            JSONObject choices = new JSONObject();
            for (Map.Entry<String, List<String>> entry : line.selections.entrySet())
                choices.put(entry.getKey(), new JSONArray(entry.getValue()));
            value.put("choices", choices); lines.put(value);
        }
        row.put("lines", lines);
        return row;
    }

    private Draft readDraft(JSONObject row, Catalog catalog) throws Exception {
        Draft draft = new Draft();
        draft.id = row.getString("id"); UUID.fromString(draft.id);
        draft.created = row.getLong("created"); draft.mode = row.getString("mode");
        if (!java.util.Arrays.asList("takeaway", "table").contains(draft.mode)) throw new IllegalStateException("Unknown mode");
        draft.table = row.getString("table"); draft.note = row.getString("note");
        if (draft.note.length() > 240 || (!draft.table.isEmpty() && !draft.table.matches("T(?:[1-9]|1[0-2])")))
            throw new IllegalStateException("Invalid saved draft");
        JSONArray lines = row.getJSONArray("lines");
        for (int i = 0; i < lines.length(); i++) {
            JSONObject value = lines.getJSONObject(i);
            Cart.Item item = catalog.byCode.get(value.getString("code"));
            if (item == null) throw new IllegalStateException("Unknown saved item");
            JSONObject raw = value.getJSONObject("choices");
            Map<String, List<String>> choices = new LinkedHashMap<>();
            java.util.Iterator<String> keys = raw.keys();
            while (keys.hasNext()) {
                String key = keys.next(); JSONArray list = raw.getJSONArray(key);
                List<String> values = new ArrayList<>();
                for (int v = 0; v < list.length(); v++) values.add(list.getString(v));
                choices.put(key, values);
            }
            draft.cart.add(item, choices, value.getInt("quantity"));
        }
        return draft;
    }
}
