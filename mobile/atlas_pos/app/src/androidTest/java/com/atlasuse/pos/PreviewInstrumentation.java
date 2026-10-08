package com.atlasuse.pos;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.Spinner;
import android.graphics.Bitmap;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Collections;

/** Runs only on the dedicated development emulator. Storage checks use a separate test database. */
public final class PreviewInstrumentation extends Instrumentation {
    @Override public void onCreate(Bundle args) { super.onCreate(args); start(); }
    private void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    @Override public void onStart() {
        Bundle result = new Bundle(); MainActivity activity = null;
        try {
            Catalog catalog = new Catalog(getTargetContext());
            check(catalog.items.size() == 63, "Expected 63 menu items");
            check(catalog.categories.size() == 9, "Expected 9 categories");
            DraftStore.State state = new DraftStore.State();
            state.active.cart.add(catalog.byCode.get("SP-001"), Collections.emptyMap(), 2);
            state.active.mode = "table"; state.active.table = "T3"; state.active.note = "Sans oignons";
            state.held.add(state.active.copy()); state.arabic = true;
            DraftStore store = new DraftStore(getTargetContext(), "atlas_preview_test_drafts.db"); store.save(state, catalog); store.close();
            store = new DraftStore(getTargetContext(), "atlas_preview_test_drafts.db"); DraftStore.State loaded = store.load(catalog);
            check(loaded.active.cart.total() == 11800 && loaded.held.size() == 1, "Restart lost quantities or held drafts");
            check(loaded.active.note.equals("Sans oignons") && loaded.active.table.equals("T3") && loaded.arabic, "Restart lost context");
            store.close();
            Intent intent = new Intent(getTargetContext(), MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity = (MainActivity) startActivitySync(intent); final MainActivity current = activity;
            runOnMainSync(() -> {
                View root = current.getWindow().getDecorView();
                root.findViewWithTag("nav_settings").performClick();
                current.getWindow().getDecorView().findViewWithTag("language_fr").performClick();
                current.getWindow().getDecorView().findViewWithTag("nav_register").performClick();
                View pizza = root.findViewWithTag("item_SP-001"); check(pizza != null, "Menu tile missing");
                long before = current.previewState().active.cart.total(); pizza.performClick();
                check(current.previewState().active.cart.total() == before + 5900, "UI add total incorrect");
                EditText search = root.findViewWithTag("search"); search.setText("not-a-product");
                check(root.findViewWithTag("item_SP-001") == null, "Search retained unrelated tile"); search.setText("");
            });
            runOnMainSync(() -> {
                View root = current.getWindow().getDecorView();
                EditText search = root.findViewWithTag("search"); search.setText("TRIO");
                root.findViewWithTag("item_SP-023").performClick();
                AlertDialog dialog = current.choicesDialog();
                check(dialog != null && dialog.isShowing(), "Meal choices did not open");
                long before = current.previewState().active.cart.total();
                dialog.getButton(AlertDialog.BUTTON_POSITIVE).performClick();
                check(dialog.isShowing() && current.previewState().active.cart.total() == before, "Incomplete meal was accepted");
                for (Cart.Group group : catalog.byCode.get("SP-023").groups) {
                    for (int slot = 0; slot < group.required; slot++) {
                        Spinner picker = dialog.getWindow().getDecorView().findViewWithTag("choice_" + group.label + "_" + slot);
                        check(picker != null, "Required choice slot missing"); picker.setSelection(1);
                    }
                }
                dialog.getButton(AlertDialog.BUTTON_POSITIVE).performClick();
                check(!dialog.isShowing() && current.previewState().active.cart.total() == before + 21900, "Completed meal total incorrect");
                search = current.getWindow().getDecorView().findViewWithTag("search"); search.setText("");
            });
            waitForIdleSync();
            capture("tablet-fr.png");
            runOnMainSync(() -> {
                View root = current.getWindow().getDecorView();
                View settings = root.findViewWithTag("nav_settings");
                if (settings != null) {
                    settings.performClick(); current.getWindow().getDecorView().findViewWithTag("language_ar").performClick();
                    check(current.previewState().arabic, "Arabic preference not set");
                    current.getWindow().getDecorView().findViewWithTag("nav_register").performClick();
                    ViewGroup content = current.findViewById(android.R.id.content);
                    check(content.getChildAt(0).getLayoutDirection() == View.LAYOUT_DIRECTION_RTL, "Arabic direction incorrect");
                }
            });
            waitForIdleSync();
            capture("tablet-ar.png");
            result.putString("stream", "PASS: 63-item catalog, 9 categories, durable drafts/notes/table/language, touch add/search, incomplete meal blocked, full meal accepted and Arabic RTL.\n");
            result.putInt("passed", 10); finish(Activity.RESULT_OK, result);
        } catch (Throwable error) {
            result.putString("stream", "FAIL: " + error.toString() + "\n"); finish(Activity.RESULT_CANCELED, result);
        }
    }
    private void capture(String name) throws Exception {
        Bitmap bitmap = getUiAutomation().takeScreenshot();
        if (bitmap == null) throw new AssertionError("Screenshot unavailable");
        try (FileOutputStream output = getTargetContext().openFileOutput(name, 0)) {
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, output);
        }
        bitmap.recycle();
    }
}
