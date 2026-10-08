package com.atlasuse.pos;

import java.math.BigDecimal;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Local draft arithmetic only. ERP prices, taxes and settlement need a server quote. */
public final class Cart {
    public static final int MAX_QUANTITY = 99;

    public static final class Group {
        public final String label;
        public final int required;
        public final List<String> choices;
        public Group(String label, int required, List<String> choices) {
            if (label.trim().isEmpty() || required < 1 || required > 20 || choices.isEmpty())
                throw new IllegalArgumentException("Invalid option group");
            this.label = label;
            this.required = required;
            this.choices = Collections.unmodifiableList(new ArrayList<>(choices));
        }
    }

    public static final class Item {
        public final String code, name, category, description;
        public final long price;
        public final List<Group> groups;
        public Item(String code, String name, String category, String description,
                    long price, List<Group> groups) {
            if (code.trim().isEmpty() || name.trim().isEmpty() || price < 0 || price > 100_000_000L)
                throw new IllegalArgumentException("Invalid menu item");
            this.code = code; this.name = name; this.category = category;
            this.description = description; this.price = price;
            this.groups = Collections.unmodifiableList(new ArrayList<>(groups));
        }
        public boolean matches(String query) {
            return normalize(code + " " + name + " " + description).contains(normalize(query));
        }
    }

    public static final class Line {
        public final Item item;
        public final Map<String, List<String>> selections;
        private int quantity;
        private Line(Item item, Map<String, List<String>> selections, int quantity) {
            this.item = item;
            Map<String, List<String>> frozen = new LinkedHashMap<>();
            selections.forEach((key, values) -> frozen.put(key, Collections.unmodifiableList(new ArrayList<>(values))));
            this.selections = Collections.unmodifiableMap(frozen);
            this.quantity = quantity;
        }
        public int quantity() { return quantity; }
        public long total() { return Math.multiplyExact(item.price, quantity); }
        public String choicesText() {
            List<String> text = new ArrayList<>();
            selections.forEach((label, values) -> text.add(label + ": " + String.join(", ", values)));
            return String.join(" · ", text);
        }
    }

    private final List<Line> lines = new ArrayList<>();
    public List<Line> lines() { return Collections.unmodifiableList(lines); }
    public boolean isEmpty() { return lines.isEmpty(); }
    public int quantity() { return lines.stream().mapToInt(Line::quantity).sum(); }
    public long total() {
        long result = 0;
        for (Line line : lines) result = Math.addExact(result, line.total());
        return result;
    }
    public void clear() { lines.clear(); }

    public void add(Item item, Map<String, List<String>> selections, int quantity) {
        validate(item, selections);
        if (quantity < 1 || quantity > MAX_QUANTITY) throw new IllegalArgumentException("Quantity limit");
        for (Line line : lines) {
            if (line.item.code.equals(item.code) && equivalent(line.selections, selections)) {
                int next = Math.addExact(line.quantity, quantity);
                if (next > MAX_QUANTITY) throw new IllegalArgumentException("Quantity limit");
                line.quantity = next;
                return;
            }
        }
        if (lines.size() >= 100) throw new IllegalArgumentException("Draft line limit");
        lines.add(new Line(item, selections, quantity));
    }

    public void change(Line line, int delta) {
        if (!lines.contains(line)) throw new IllegalArgumentException("Unknown cart line");
        int next = Math.addExact(line.quantity, delta);
        if (next > MAX_QUANTITY || next < 0) throw new IllegalArgumentException("Quantity limit");
        if (next == 0) lines.remove(line); else line.quantity = next;
    }

    public Cart copy() {
        Cart result = new Cart();
        for (Line line : lines) result.add(line.item, line.selections, line.quantity);
        return result;
    }

    public static void validate(Item item, Map<String, List<String>> selections) {
        if (selections.size() != item.groups.size()) throw new IllegalArgumentException("Required choices");
        for (Group group : item.groups) {
            List<String> selected = selections.get(group.label);
            if (selected == null || selected.size() != group.required || !group.choices.containsAll(selected))
                throw new IllegalArgumentException("Required choices: " + group.label);
        }
    }

    // The order of drink/pizza slots must not create otherwise identical lines.
    private static boolean equivalent(Map<String, List<String>> left, Map<String, List<String>> right) {
        if (!left.keySet().equals(right.keySet())) return false;
        for (String key : left.keySet()) {
            List<String> a = new ArrayList<>(left.get(key)), b = new ArrayList<>(right.get(key));
            Collections.sort(a); Collections.sort(b);
            if (!a.equals(b)) return false;
        }
        return true;
    }

    public static long minorUnits(String value) {
        return new BigDecimal(value).movePointRight(2).longValueExact();
    }
    public static String money(long minor) {
        return String.format(Locale.FRANCE, "%,.2f MAD", minor / 100.0);
    }
    public static String normalize(String value) {
        return Normalizer.normalize(value, Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "").toLowerCase(Locale.ROOT).trim();
    }
}
