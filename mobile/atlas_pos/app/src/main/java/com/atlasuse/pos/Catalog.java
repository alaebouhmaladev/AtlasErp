package com.atlasuse.pos;

import android.content.Context;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;

final class Catalog {
    final List<Cart.Item> items = new ArrayList<>();
    final List<String> categories = new ArrayList<>();
    final Map<String, Cart.Item> byCode = new LinkedHashMap<>();
    final String capturedOn, hash;

    Catalog(Context context) throws Exception {
        byte[] bytes;
        try (InputStream stream = context.getAssets().open("streetpizza-menu.json")) {
            java.io.ByteArrayOutputStream output = new java.io.ByteArrayOutputStream();
            byte[] buffer = new byte[8192]; int count;
            while ((count = stream.read(buffer)) != -1) output.write(buffer, 0, count);
            bytes = output.toByteArray();
        }
        StringBuilder digest = new StringBuilder();
        for (byte part : MessageDigest.getInstance("SHA-256").digest(bytes))
            digest.append(String.format(java.util.Locale.ROOT, "%02x", part & 0xff));
        hash = digest.toString();
        JSONObject root = new JSONObject(new String(bytes, StandardCharsets.UTF_8));
        if (!"MAD".equals(root.getString("currency"))) throw new IllegalArgumentException("Unsupported demo currency");
        capturedOn = root.getString("captured_on");
        JSONArray rows = root.getJSONArray("items");
        LinkedHashSet<String> names = new LinkedHashSet<>();
        for (int i = 0; i < rows.length(); i++) {
            JSONObject row = rows.getJSONObject(i);
            List<Cart.Group> groups = new ArrayList<>();
            JSONArray options = row.getJSONArray("options");
            for (int g = 0; g < options.length(); g++) {
                JSONObject option = options.getJSONObject(g);
                JSONArray values = option.getJSONArray("choices");
                List<String> choices = new ArrayList<>();
                for (int c = 0; c < values.length(); c++) choices.add(values.getString(c));
                groups.add(new Cart.Group(option.getString("label"), option.getInt("required_count"), choices));
            }
            Cart.Item item = new Cart.Item(row.getString("item_code"), row.getString("item_name"),
                row.getString("category"), row.optString("description"),
                Cart.minorUnits(row.get("price_mad").toString()), groups);
            if (byCode.put(item.code, item) != null) throw new IllegalArgumentException("Duplicate catalog code");
            items.add(item); names.add(item.category);
        }
        categories.addAll(names);
        if (items.isEmpty()) throw new IllegalArgumentException("Empty catalog");
    }
}
