package com.atlasuse.pos;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.text.InputFilter;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Android UI foundation. All tickets are local drafts, never invoices or kitchen commands. */
public final class MainActivity extends Activity {
    private static final int GREEN = Color.rgb(20, 63, 53), LIME = Color.rgb(225, 245, 164);
    private static final int BG = Color.rgb(246, 248, 244), MUTED = Color.rgb(106, 125, 116);
    private static final int BORDER = Color.rgb(223, 230, 223), WHITE = Color.WHITE;
    private Catalog catalog;
    private DraftStore store;
    private DraftStore.State state;
    private LinearLayout root, main, cartPanel;
    private LinearLayout menuGrid;
    private String screen = "register", category = "", query = "";
    private boolean healthy = true, compact;
    private AlertDialog compactDialog;
    private AlertDialog optionDialog;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        try {
            catalog = new Catalog(this); store = new DraftStore(this); state = store.load(catalog);
            if (saved != null) {
                screen = saved.getString("screen", "register");
                category = saved.getString("category", ""); query = saved.getString("query", "");
            }
            render();
        } catch (Exception error) {
            healthy = false;
            TextView message = text("ATLAS POS\nImpossible de lire les brouillons. Les données sont conservées.\nContactez le support avant de réinstaller.", 20, GREEN, true);
            message.setPadding(dp(32), dp(64), dp(32), dp(32)); setContentView(message);
        }
    }
    @Override protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        out.putString("screen", screen); out.putString("category", category); out.putString("query", query);
    }
    @Override protected void onDestroy() { if (store != null) store.close(); super.onDestroy(); }
    DraftStore.State previewState() { return state; }
    AlertDialog choicesDialog() { return optionDialog; }

    private String t(String fr, String ar) { return state.arabic ? ar : fr; }
    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private LinearLayout column() {
        LinearLayout view = new LinearLayout(this); view.setOrientation(LinearLayout.VERTICAL); return view;
    }
    private LinearLayout row() {
        LinearLayout view = new LinearLayout(this); view.setOrientation(LinearLayout.HORIZONTAL); view.setGravity(Gravity.CENTER_VERTICAL); return view;
    }
    private GradientDrawable background(int color, int radius, boolean border) {
        GradientDrawable drawable = new GradientDrawable(); drawable.setColor(color); drawable.setCornerRadius(dp(radius));
        if (border) drawable.setStroke(dp(1), BORDER); return drawable;
    }
    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this); view.setText(value); view.setTextSize(size); view.setTextColor(color);
        if (bold) view.setTypeface(Typeface.create("sans-serif-medium", Typeface.NORMAL));
        return view;
    }
    private Button button(String label, boolean primary, Runnable action) {
        Button view = new Button(this); view.setText(label); view.setTextSize(14); view.setAllCaps(false);
        view.setTextColor(GREEN); view.setMinHeight(dp(48)); view.setMinimumHeight(dp(48));
        view.setPadding(dp(12), dp(8), dp(12), dp(8));
        view.setBackground(background(primary ? LIME : WHITE, 12, !primary));
        view.setOnClickListener(v -> { if (healthy) action.run(); }); return view;
    }
    private void gap(LinearLayout parent, int height) { parent.addView(new View(this), new LinearLayout.LayoutParams(1, dp(height))); }
    private void weighted(LinearLayout parent, View child) { parent.addView(child, new LinearLayout.LayoutParams(0, -2, 1)); }
    private ScrollView scroll(View content) {
        ScrollView view = new ScrollView(this); view.setFillViewport(true); view.addView(content); return view;
    }
    private void toast(String message) { Toast.makeText(this, message, Toast.LENGTH_SHORT).show(); }
    private boolean persist() {
        try { store.save(state, catalog); return true; }
        catch (Exception error) {
            healthy = false;
            new AlertDialog.Builder(this).setTitle(t("Stockage indisponible", "التخزين غير متاح"))
                .setMessage(t("La dernière modification n’est pas enregistrée. Arrêtez la saisie et contactez le support. Les anciens brouillons sont conservés.",
                    "لم يتم حفظ آخر تعديل. أوقف الإدخال واتصل بالدعم. تم الاحتفاظ بالمسودات السابقة."))
                .setCancelable(false).setPositiveButton("OK", (dialog, which) -> finish()).show();
            return false;
        }
    }
    private void go(String destination) { screen = destination; render(); }

    private void render() {
        if (compactDialog != null) { compactDialog.dismiss(); compactDialog = null; }
        menuGrid = null; cartPanel = null;
        compact = getResources().getConfiguration().screenWidthDp < 900;
        root = column(); root.setBackgroundColor(BG);
        root.setLayoutDirection(state.arabic ? View.LAYOUT_DIRECTION_RTL : View.LAYOUT_DIRECTION_LTR);
        // API 35 edge-to-edge: apply real system bar insets instead of guessing tablet padding.
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets;
        });
        setContentView(root); root.requestApplyInsets();
        header();
        LinearLayout body = row(); body.setGravity(Gravity.TOP);
        root.addView(body, new LinearLayout.LayoutParams(-1, 0, 1));
        if (!compact) body.addView(navigation(), new LinearLayout.LayoutParams(dp(106), -1));
        main = column(); main.setPadding(dp(20), dp(18), dp(20), dp(12));
        body.addView(main, new LinearLayout.LayoutParams(0, -1, 1));
        if (compact) mobileNavigation();
        if (screen.equals("register")) register(body);
        else if (screen.equals("tables")) tables();
        else if (screen.equals("drafts")) drafts();
        else settings();
    }

    private void header() {
        LinearLayout top = row(); top.setPadding(dp(20), dp(12), dp(20), dp(12)); top.setBackgroundColor(WHITE);
        ImageView logo = new ImageView(this); logo.setImageResource(com.atlasuse.pos.R.drawable.atlas_icon);
        top.addView(logo, new LinearLayout.LayoutParams(dp(38), dp(38)));
        TextView brand = text("ATLAS POS", 19, GREEN, true); brand.setPadding(dp(10), 0, dp(10), 0); top.addView(brand);
        TextView business = text(compact ? "Street Pizza" : "Street Pizza · Maarif", 15, GREEN, false);
        top.addView(business, new LinearLayout.LayoutParams(0, -2, 1));
        TextView status = text(t("APERÇU LOCAL", "معاينة محلية"), 11, GREEN, true);
        status.setPadding(dp(14), dp(9), dp(14), dp(9)); status.setBackground(background(LIME, 20, false)); top.addView(status);
        root.addView(top, new LinearLayout.LayoutParams(-1, dp(66)));
    }

    private LinearLayout navigation() {
        LinearLayout nav = column(); nav.setPadding(dp(10), dp(18), dp(10), dp(16)); nav.setBackgroundColor(WHITE);
        String[] keys = {"register", "tables", "drafts", "settings"};
        String[] labels = {t("Caisse", "الصندوق"), t("Tables", "الطاولات"), t("Brouillons", "المسودات"), t("Réglages", "الإعدادات")};
        String[] glyphs = {"▦", "◫", "≡", "⚙"};
        for (int i = 0; i < keys.length; i++) {
            final String key = keys[i];
            Button choice = button(glyphs[i] + "\n" + labels[i], screen.equals(key), () -> go(key));
            choice.setTextSize(12); choice.setGravity(Gravity.CENTER); choice.setTag("nav_" + key);
            choice.setBackground(background(screen.equals(key) ? LIME : WHITE, 12, false));
            nav.addView(choice, new LinearLayout.LayoutParams(-1, dp(76))); gap(nav, 8);
        }
        nav.addView(new View(this), new LinearLayout.LayoutParams(1, 0, 1));
        TextView version = text("0.1\nPREVIEW", 10, MUTED, false); version.setGravity(Gravity.CENTER); nav.addView(version);
        return nav;
    }

    private void mobileNavigation() {
        LinearLayout buttons = row();
        String[] keys = {"register", "tables", "drafts", "settings"};
        String[] labels = {t("Caisse", "الصندوق"), t("Tables", "الطاولات"), t("Tickets", "المسودات"), "⚙"};
        for (int i = 0; i < keys.length; i++) {
            final String key = keys[i]; Button choice = button(labels[i], screen.equals(key), () -> go(key));
            choice.setTag("nav_" + key); weighted(buttons, choice);
        }
        main.addView(buttons); gap(main, 12);
    }

    private void register(LinearLayout body) {
        LinearLayout heading = row();
        weighted(heading, text(t("Une bonne journée commence ici.", "يوم جيد يبدأ هنا."), compact ? 20 : 25, GREEN, true));
        if (compact) {
            Button open = button(t("Panier", "السلة") + " (" + state.active.cart.quantity() + ")", true, this::showCompactCart);
            open.setTag("open_cart"); heading.addView(open);
        }
        main.addView(heading); gap(main, 5);
        main.addView(text(t("63 produits · prix de démonstration · " + catalog.capturedOn,
            "63 منتجًا · أسعار تجريبية · " + catalog.capturedOn), 12, MUTED, false)); gap(main, 14);
        LinearLayout tools = row();
        EditText search = new EditText(this); search.setSingleLine(); search.setTextSize(15); search.setTextColor(GREEN);
        search.setHint(t("Rechercher un produit ou un code…", "ابحث عن منتج أو رمز…")); search.setText(query);
        search.setPadding(dp(16), dp(10), dp(12), dp(10)); search.setBackground(background(WHITE, 12, true));
        search.setTag("search"); weighted(tools, search);
        Button clear = button("×", false, () -> search.setText("")); clear.setContentDescription(t("Effacer la recherche", "مسح البحث")); tools.addView(clear);
        main.addView(tools); gap(main, 12);
        HorizontalScrollView categories = new HorizontalScrollView(this); categories.setHorizontalScrollBarEnabled(false);
        LinearLayout chips = row(); addCategory(chips, "", t("Tout le menu", "كل القائمة"));
        for (String name : catalog.categories) addCategory(chips, name, shortCategory(name));
        categories.addView(chips); main.addView(categories); gap(main, 12);
        menuGrid = column();
        ScrollView menu = scroll(menuGrid); main.addView(menu, new LinearLayout.LayoutParams(-1, 0, 1));
        populateMenu();
        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) { query = s.toString(); populateMenu(); }
            public void afterTextChanged(Editable e) {}
        });
        gap(main, 10);
        main.addView(text(t("Brouillons sauvegardés sur cet appareil. Aucun encaissement ni envoi en cuisine.",
            "تُحفظ المسودات على هذا الجهاز. لا يتم تحصيل الدفع أو إرسال الطلبات للمطبخ."), 11, MUTED, false));
        if (!compact) {
            cartPanel = column(); cartPanel.setPadding(dp(20), dp(22), dp(20), dp(20)); cartPanel.setBackgroundColor(WHITE);
            body.addView(cartPanel, new LinearLayout.LayoutParams(dp(330), -1)); drawCart(cartPanel);
        }
    }

    private void addCategory(LinearLayout chips, String key, String label) {
        Button chip = button(label, category.equals(key), () -> { category = key; render(); });
        chip.setTextSize(12); chip.setTag("category_" + key);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-2, dp(48)); params.setMarginEnd(dp(8)); chips.addView(chip, params);
    }
    private String shortCategory(String name) {
        if (name.contains("PIZZAS")) return t("Pizzas", "بيتزا");
        if (name.contains("FORMULES")) return t("Formules", "وجبات");
        if (name.contains("SALADES")) return t("Salades", "سلطات");
        if (name.contains("BURGER")) return t("Burgers", "برغر");
        if (name.contains("PÂTES")) return t("Pâtes", "معكرونة");
        if (name.contains("SANDWICH")) return t("Sandwichs", "ساندويتش");
        if (name.contains("DESSERT")) return t("Desserts", "حلويات");
        if (name.contains("JUS")) return t("Jus frais", "عصائر");
        return t("Boissons", "مشروبات");
    }
    private void populateMenu() {
        if (menuGrid == null) return; menuGrid.removeAllViews();
        int matches = 0;
        int columns = compact ? 2 : 3;
        LinearLayout gridRow = null;
        for (Cart.Item item : catalog.items) {
            if ((!category.isEmpty() && !category.equals(item.category)) || !item.matches(query)) continue;
            matches++;
            LinearLayout card = column(); card.setPadding(dp(16), dp(16), dp(16), dp(12));
            card.setBackground(background(WHITE, 14, true)); card.setMinimumHeight(dp(164));
            TextView icon = text(item.category.contains("PIZZAS") ? "P" : item.name.substring(0, 1), 19, GREEN, true);
            icon.setGravity(Gravity.CENTER); icon.setBackground(background(LIME, 10, false));
            card.addView(icon, new LinearLayout.LayoutParams(dp(38), dp(38))); gap(card, 12);
            TextView name = text(item.name, 14, GREEN, true); name.setMaxLines(2);
            card.addView(name, new LinearLayout.LayoutParams(-1, dp(40))); gap(card, 6);
            LinearLayout price = row(); price.setLayoutDirection(View.LAYOUT_DIRECTION_LTR); weighted(price, text(Cart.money(item.price), 15, GREEN, true));
            price.addView(text(item.groups.isEmpty() ? "+" : "⋯", 22, GREEN, true)); card.addView(price);
            card.setContentDescription(item.name + ", " + Cart.money(item.price)); card.setFocusable(true);
            card.setTag("item_" + item.code); card.setOnClickListener(v -> { if (healthy) choose(item); });
            if ((matches - 1) % columns == 0) {
                gridRow = row(); gridRow.setGravity(Gravity.TOP); menuGrid.addView(gridRow);
            }
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, -2, 1);
            params.setMargins(dp(4), dp(4), dp(4), dp(4)); gridRow.addView(card, params);
        }
        if (matches == 0) menuGrid.addView(text(t("Aucun produit trouvé.", "لم يتم العثور على منتجات."), 16, MUTED, false));
        else if (matches % columns != 0) {
            for (int i = matches % columns; i < columns; i++) gridRow.addView(new View(this), new LinearLayout.LayoutParams(0, 1, 1));
        }
    }

    private void choose(Cart.Item item) {
        if (item.groups.isEmpty()) { add(item, Collections.emptyMap()); return; }
        LinearLayout fields = column(); fields.setPadding(dp(22), dp(12), dp(22), dp(12));
        fields.addView(text(item.description, 13, MUTED, false));
        Map<String, List<Spinner>> slots = new LinkedHashMap<>();
        for (Cart.Group group : item.groups) {
            gap(fields, 14); fields.addView(text(group.label + " · " + group.required + t(" choix requis", " اختيارات مطلوبة"), 15, GREEN, true));
            List<Spinner> selections = new ArrayList<>();
            for (int i = 0; i < group.required; i++) {
                Spinner picker = new Spinner(this); List<String> choices = new ArrayList<>();
                choices.add(t("Choisir…", "اختر…")); choices.addAll(group.choices);
                ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, choices);
                adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item); picker.setAdapter(adapter);
                picker.setTag("choice_" + group.label + "_" + i); picker.setContentDescription(group.label + " " + (i + 1));
                fields.addView(picker, new LinearLayout.LayoutParams(-1, dp(52))); selections.add(picker);
            }
            slots.put(group.label, selections);
        }
        AlertDialog dialog = new AlertDialog.Builder(this).setTitle(item.name).setView(scroll(fields))
            .setNegativeButton(t("Annuler", "إلغاء"), null).setPositiveButton(t("Ajouter", "إضافة"), null).create();
        optionDialog = dialog;
        dialog.show();
        dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            Map<String, List<String>> selections = new LinkedHashMap<>();
            for (Map.Entry<String, List<Spinner>> entry : slots.entrySet()) {
                List<String> selected = new ArrayList<>();
                for (Spinner picker : entry.getValue()) {
                    if (picker.getSelectedItemPosition() == 0) { toast(t("Complétez tous les choix requis.", "أكمل جميع الاختيارات المطلوبة.")); return; }
                    selected.add((String) picker.getSelectedItem());
                }
                selections.put(entry.getKey(), selected);
            }
            if (add(item, selections)) dialog.dismiss();
        });
    }
    private boolean add(Cart.Item item, Map<String, List<String>> selections) {
        try {
            state.active.cart.add(item, selections, 1);
            if (!persist()) return false;
            if (compact) { toast(item.name + t(" ajouté", " تمت الإضافة")); render(); }
            else drawCart(cartPanel);
            return true;
        } catch (IllegalArgumentException error) { toast(t("Limite du brouillon atteinte.", "تم الوصول إلى حد المسودة.")); return false; }
    }

    private String service(DraftStore.Draft draft) {
        return draft.mode.equals("table") ? t("Sur place", "في المطعم") + (draft.table.isEmpty() ? "" : " · " + draft.table) : t("À emporter", "للأخذ");
    }
    private void drawCart(LinearLayout panel) {
        panel.removeAllViews();
        LinearLayout heading = row(); weighted(heading, text(t("Commande", "الطلب"), 22, GREEN, true));
        heading.addView(text(t("BROUILLON", "مسودة"), 10, MUTED, true)); panel.addView(heading); gap(panel, 12);
        LinearLayout modes = row();
        Button takeaway = button(t("À emporter", "للأخذ"), state.active.mode.equals("takeaway"), () -> {
            state.active.mode = "takeaway"; state.active.table = ""; if (persist()) drawCart(panel);
        }); takeaway.setTag("mode_takeaway"); weighted(modes, takeaway);
        Button dinein = button(t("Sur place", "في المطعم"), state.active.mode.equals("table"), () -> selectTable(panel));
        dinein.setTag("mode_table"); weighted(modes, dinein); panel.addView(modes); gap(panel, 8);
        panel.addView(text(service(state.active), 12, MUTED, false)); gap(panel, 12);
        LinearLayout lines = column();
        if (state.active.cart.isEmpty()) {
            gap(lines, 36); lines.addView(text(t("Votre panier vous attend.", "سلتك في انتظارك."), 17, GREEN, true)); gap(lines, 8);
            lines.addView(text(t("Touchez un produit pour commencer.", "اضغط على منتج للبدء."), 13, MUTED, false));
        }
        for (Cart.Line line : state.active.cart.lines()) {
            LinearLayout item = column(); item.setPadding(0, dp(8), 0, dp(12));
            item.addView(text(line.item.name, 14, GREEN, true));
            if (!line.selections.isEmpty()) { gap(item, 5); item.addView(text(line.choicesText(), 11, MUTED, false)); }
            gap(item, 8); LinearLayout controls = row();
            Button minus = button("−", false, () -> adjust(line, -1, panel)); minus.setTag("minus_" + line.item.code);
            minus.setContentDescription(t("Retirer une unité de ", "إنقاص وحدة من ") + line.item.name);
            controls.addView(minus, new LinearLayout.LayoutParams(dp(48), dp(48)));
            TextView count = text(Integer.toString(line.quantity()), 15, GREEN, true); count.setGravity(Gravity.CENTER);
            controls.addView(count, new LinearLayout.LayoutParams(dp(38), -2));
            Button plus = button("+", false, () -> adjust(line, 1, panel)); plus.setTag("plus_" + line.item.code);
            plus.setContentDescription(t("Ajouter une unité de ", "زيادة وحدة من ") + line.item.name);
            controls.addView(plus, new LinearLayout.LayoutParams(dp(48), dp(48)));
            TextView amount = text(Cart.money(line.total()), 13, GREEN, true); amount.setGravity(Gravity.END);
            weighted(controls, amount); item.addView(controls); lines.addView(item);
            View divider = new View(this); divider.setBackgroundColor(BORDER); lines.addView(divider, new LinearLayout.LayoutParams(-1, dp(1)));
        }
        panel.addView(scroll(lines), new LinearLayout.LayoutParams(-1, 0, 1)); gap(panel, 12);
        Button notes = button(state.active.note.isEmpty() ? t("+ Note de commande", "+ ملاحظة الطلب") : state.active.note, false, () -> editNote(panel));
        notes.setTag("edit_note"); panel.addView(notes); gap(panel, 12);
        LinearLayout total = row(); weighted(total, text(t("Total du menu", "إجمالي القائمة"), 13, MUTED, false));
        TextView value = text(Cart.money(state.active.cart.total()), 22, GREEN, true); value.setTag("cart_total"); total.addView(value);
        panel.addView(total); gap(panel, 4);
        panel.addView(text(t("Prix publics démo. Taxes non calculées par l’ERP.", "أسعار تجريبية عامة. لم يحسب النظام الضرائب."), 10, MUTED, false)); gap(panel, 12);
        Button save = button(t("Mettre en attente", "حفظ المسودة"), true, () -> hold(true));
        save.setTag("hold_draft"); save.setEnabled(!state.active.cart.isEmpty()); panel.addView(save, new LinearLayout.LayoutParams(-1, dp(52))); gap(panel, 8);
        Button payment = button(t("Encaissement · étape suivante", "الدفع · المرحلة التالية"), false, this::paymentStatus);
        payment.setTag("payment_status"); panel.addView(payment);
        TextView clear = text(t("Vider ce panier", "إفراغ هذه السلة"), 12, MUTED, false);
        clear.setPadding(0, dp(14), 0, dp(2)); clear.setTag("clear_cart"); clear.setOnClickListener(v -> {
            if (!healthy || state.active.cart.isEmpty()) return;
            new AlertDialog.Builder(this).setTitle(t("Vider le brouillon actif ?", "إفراغ المسودة الحالية؟"))
                .setMessage(t("Les tickets déjà mis en attente sont conservés.", "يتم الاحتفاظ بالمسودات المحفوظة."))
                .setNegativeButton(t("Garder", "احتفاظ"), null).setPositiveButton(t("Vider", "إفراغ"), (d, w) -> {
                    state.active = new DraftStore.Draft(); if (persist()) drawCart(panel);
                }).show();
        }); panel.addView(clear);
    }
    private void adjust(Cart.Line line, int delta, LinearLayout panel) {
        try { state.active.cart.change(line, delta); if (persist()) drawCart(panel); }
        catch (IllegalArgumentException error) { toast(t("Maximum : 99 unités.", "الحد الأقصى: 99 وحدة.")); }
    }
    private void selectTable(LinearLayout panel) {
        String[] labels = new String[12]; for (int i = 0; i < 12; i++) labels[i] = "T" + (i + 1);
        new AlertDialog.Builder(this).setTitle(t("Table du brouillon local", "طاولة المسودة المحلية"))
            .setItems(labels, (d, index) -> {
                state.active.mode = "table"; state.active.table = labels[index]; if (persist()) drawCart(panel);
            }).setNegativeButton(t("Annuler", "إلغاء"), null).show();
    }
    private void editNote(LinearLayout panel) {
        EditText input = new EditText(this); input.setText(state.active.note); input.setFilters(new InputFilter[]{new InputFilter.LengthFilter(240)});
        input.setHint(t("Ex. sans oignons", "مثال: بدون بصل")); input.setTag("note_input");
        new AlertDialog.Builder(this).setTitle(t("Note du brouillon", "ملاحظة المسودة")).setView(input)
            .setNegativeButton(t("Annuler", "إلغاء"), null).setPositiveButton(t("Enregistrer", "حفظ"), (d, w) -> {
                state.active.note = input.getText().toString().trim(); if (persist()) drawCart(panel);
            }).show();
    }
    private void showCompactCart() {
        LinearLayout panel = column(); panel.setPadding(dp(20), dp(18), dp(20), dp(18));
        int height = Math.max(360, getResources().getConfiguration().screenHeightDp - 160);
        FrameLayout frame = new FrameLayout(this); frame.addView(panel, new FrameLayout.LayoutParams(-1, dp(height)));
        drawCart(panel);
        compactDialog = new AlertDialog.Builder(this).setView(frame)
            .setNegativeButton(t("Retour au menu", "العودة للقائمة"), (d, w) -> render()).create();
        compactDialog.setOnCancelListener(d -> render()); compactDialog.show();
    }
    private void hold(boolean refresh) {
        if (state.active.cart.isEmpty()) return;
        if (state.held.size() >= 50) { toast(t("50 brouillons maximum. Supprimez un ancien ticket.", "الحد الأقصى 50 مسودة. احذف مسودة قديمة.")); return; }
        state.held.add(0, state.active.copy()); state.active = new DraftStore.Draft();
        if (persist()) { if (refresh) render(); toast(t("Brouillon enregistré sur cet appareil.", "تم حفظ المسودة على هذا الجهاز.")); }
    }
    private void paymentStatus() {
        new AlertDialog.Builder(this).setTitle(t("Encaissement à connecter", "ربط الدفع مطلوب"))
            .setMessage(t("Cet aperçu n’enregistre aucune vente. La prochaine étape reliera l’appareil, le caissier et le registre à ATLASERP, puis ajoutera les ventes espèces hors ligne. Les paiements NAPS seront enregistrés après validation sur votre TPE.",
                "هذه المعاينة لا تسجل أي مبيعات. المرحلة التالية تربط الجهاز والكاشير والصندوق بالنظام ثم تضيف البيع النقدي دون إنترنت. تُسجل مدفوعات NAPS بعد الموافقة على جهاز الدفع."))
            .setPositiveButton("OK", null).show();
    }

    private void pageTitle(String title, String subtitle) {
        main.addView(text(title, 28, GREEN, true)); gap(main, 6); main.addView(text(subtitle, 13, MUTED, false)); gap(main, 24);
    }
    private void tables() {
        pageTitle(t("Chaque table a sa place.", "مكان لكل طاولة."),
            t("Plan démo · associez une table au panier local · aucune occupation partagée", "مخطط تجريبي · اربط طاولة بالسلة المحلية · بدون مزامنة إشغال الطاولات"));
        LinearLayout grid = column(); LinearLayout gridRow = null; int columns = compact ? 2 : 4;
        for (int i = 1; i <= 12; i++) {
            String table = "T" + i;
            long count = state.held.stream().filter(d -> table.equals(d.table)).count();
            Button choice = button(table + "\n" + count + t(" brouillon(s) local(aux)", " مسودات محلية"), table.equals(state.active.table), () -> {
                state.active.mode = "table"; state.active.table = table; if (persist()) go("register");
            }); choice.setTag("table_" + table);
            if ((i - 1) % columns == 0) { gridRow = row(); grid.addView(gridRow); }
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(120), 1);
            params.setMargins(dp(6), dp(6), dp(6), dp(6)); gridRow.addView(choice, params);
        }
        main.addView(scroll(grid), new LinearLayout.LayoutParams(-1, 0, 1));
    }
    private void drafts() {
        pageTitle(t("Retrouvez vos brouillons.", "استرجع مسوداتك."),
            t("Enregistrés sur cet appareil · aucun ticket encaissé ou envoyé en cuisine", "محفوظة على هذا الجهاز · بدون تحصيل دفع أو إرسال للمطبخ"));
        LinearLayout list = column();
        if (state.held.isEmpty()) list.addView(text(t("Aucun brouillon en attente.", "لا توجد مسودات محفوظة."), 18, MUTED, false));
        for (DraftStore.Draft draft : state.held) {
            LinearLayout card = column(); card.setPadding(dp(20), dp(18), dp(20), dp(18)); card.setBackground(background(WHITE, 14, true));
            LinearLayout title = row(); weighted(title, text(service(draft), 19, GREEN, true)); title.addView(text(Cart.money(draft.cart.total()), 19, GREEN, true)); card.addView(title);
            gap(card, 8); card.addView(text(new SimpleDateFormat("dd/MM · HH:mm", Locale.FRANCE).format(new Date(draft.created))
                + " · " + draft.cart.quantity() + t(" article(s)", " منتجات"), 12, MUTED, false));
            if (!draft.note.isEmpty()) { gap(card, 5); card.addView(text(draft.note, 13, GREEN, false)); }
            gap(card, 12); LinearLayout actions = row();
            Button restore = button(t("Reprendre", "استرجاع"), true, () -> restore(draft)); restore.setTag("restore_" + draft.id); weighted(actions, restore);
            actions.addView(button(t("Supprimer", "حذف"), false, () -> new AlertDialog.Builder(this)
                .setTitle(t("Supprimer ce brouillon ?", "حذف هذه المسودة؟"))
                .setNegativeButton(t("Garder", "احتفاظ"), null).setPositiveButton(t("Supprimer", "حذف"), (d, w) -> {
                    state.held.remove(draft); if (persist()) render();
                }).show())); card.addView(actions); list.addView(card); gap(list, 12);
        }
        main.addView(scroll(list), new LinearLayout.LayoutParams(-1, 0, 1));
    }
    private void restore(DraftStore.Draft draft) {
        // Move the held draft into editing and hold the current cart in the same DB snapshot.
        state.held.remove(draft);
        if (!state.active.cart.isEmpty()) state.held.add(0, state.active.copy());
        state.active = draft.copy(); if (persist()) go("register");
    }
    private void settings() {
        pageTitle(t("Votre espace ATLAS.", "مساحتك في أطلس."), t("Android · interface native · aperçu 0.1", "أندرويد · واجهة أصلية · معاينة 0.1"));
        LinearLayout content = column();
        content.addView(text(t("Langue de l’interface", "لغة الواجهة"), 18, GREEN, true)); gap(content, 12);
        LinearLayout languages = row();
        Button fr = button("Français", !state.arabic, () -> { state.arabic = false; if (persist()) render(); }); fr.setTag("language_fr"); weighted(languages, fr);
        Button ar = button("العربية", state.arabic, () -> { state.arabic = true; if (persist()) render(); }); ar.setTag("language_ar"); weighted(languages, ar); content.addView(languages);
        gap(content, 24); content.addView(text(t("Le catalogue de démonstration", "القائمة التجريبية"), 18, GREEN, true)); gap(content, 8);
        content.addView(text(t("63 produits Street Pizza · " + catalog.capturedOn + "\nSource publique : streetpizza.ma\nCes prix ne sont pas synchronisés avec le registre.",
            "63 منتجًا من Street Pizza · " + catalog.capturedOn + "\nالمصدر العام: streetpizza.ma\nهذه الأسعار غير متزامنة مع الصندوق."), 14, MUTED, false));
        gap(content, 24); content.addView(text(t("Prochaines connexions", "الروابط القادمة"), 18, GREEN, true)); gap(content, 8);
        content.addView(text(t("• Connexion sécurisée et caisse assignée\n• Ventes espèces et file de synchronisation\n• Imprimantes, cuisine et écrans sur le même routeur\n• Tables, notes cuisine et partage de l’addition\n• NAPS : validation sur le TPE, puis saisie de la référence",
            "• اتصال آمن وصندوق مخصص\n• البيع النقدي وقائمة المزامنة\n• الطابعات والمطبخ والشاشات عبر نفس الراوتر\n• الطاولات وملاحظات المطبخ وتقسيم الفاتورة\n• NAPS: الموافقة على الجهاز ثم إدخال المرجع"), 14, MUTED, false));
        gap(content, 24); content.addView(text(t("Outils web existants", "أدوات الويب الحالية"), 18, GREEN, true)); gap(content, 12);
        content.addView(button(t("Ouvrir le backoffice ATLASERP ↗", "فتح لوحة الإدارة ↗"), false, () -> openWeb("https://erp.atlasuse.site/atlas"))); gap(content, 8);
        content.addView(button(t("Voir le menu public ↗", "عرض القائمة العامة ↗"), false, () -> openWeb("https://erp.atlasuse.site/atlas-menu")));
        gap(content, 18); content.addView(text(t("Aucune permission réseau ni donnée de paiement dans cette version. Ne désinstallez pas l’app si vous souhaitez garder vos brouillons.",
            "هذا الإصدار لا يطلب إذن الشبكة ولا يخزن بيانات الدفع. لا تحذف التطبيق إذا أردت الاحتفاظ بمسوداتك."), 12, MUTED, false));
        main.addView(scroll(content), new LinearLayout.LayoutParams(-1, 0, 1));
    }
    private void openWeb(String url) {
        try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }
        catch (android.content.ActivityNotFoundException error) { toast(t("Aucun navigateur disponible.", "لا يوجد متصفح متاح.")); }
    }
}
