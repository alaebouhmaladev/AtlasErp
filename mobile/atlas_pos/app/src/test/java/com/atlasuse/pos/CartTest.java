package com.atlasuse.pos;

import org.junit.Test;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.List;
import static org.junit.Assert.*;

public final class CartTest {
    private Cart.Item pizza() { return new Cart.Item("SP-001", "LA MARINARA", "PIZZAS", "Tomate", 5900, Collections.emptyList()); }
    private Cart.Item meal() {
        return new Cart.Item("SP-023", "TRIO", "FORMULES", "", 21900, Arrays.asList(
            new Cart.Group("Boissons", 3, Arrays.asList("Eau", "Cola")),
            new Cart.Group("Pizzas", 2, Arrays.asList("Marinara", "Veggie"))));
    }
    private Map<String, List<String>> choices(String... pizzas) {
        Map<String, List<String>> choices = new LinkedHashMap<>();
        choices.put("Boissons", Arrays.asList("Eau", "Cola", "Eau")); choices.put("Pizzas", Arrays.asList(pizzas)); return choices;
    }
    @Test public void madUsesExactMinorUnits() {
        assertEquals(30100, Cart.minorUnits("301.00"));
        assertEquals(10, Cart.minorUnits("0.10"));
        assertThrows(ArithmeticException.class, () -> Cart.minorUnits("1.001"));
    }
    @Test public void incompleteAndUnknownMealChoicesAreRejected() {
        Cart cart = new Cart();
        assertThrows(IllegalArgumentException.class, () -> cart.add(meal(), Collections.emptyMap(), 1));
        assertThrows(IllegalArgumentException.class, () -> cart.add(meal(), choices("Marinara"), 1));
        assertThrows(IllegalArgumentException.class, () -> cart.add(meal(), choices("Marinara", "Unknown"), 1));
        assertTrue(cart.isEmpty());
    }
    @Test public void equivalentChoicesMergeButDifferentMealsRemainSeparate() {
        Cart cart = new Cart();
        cart.add(meal(), choices("Marinara", "Veggie"), 1);
        cart.add(meal(), choices("Veggie", "Marinara"), 1);
        cart.add(meal(), choices("Veggie", "Veggie"), 1);
        assertEquals(2, cart.lines().size()); assertEquals(3, cart.quantity()); assertEquals(65700, cart.total());
    }
    @Test public void restartSnapshotCopyCannotMutateTheHeldCart() {
        Cart active = new Cart(); active.add(pizza(), Collections.emptyMap(), 2);
        Cart held = active.copy(); active.change(active.lines().get(0), -1);
        assertEquals(11800, held.total()); assertEquals(5900, active.total());
        active.change(active.lines().get(0), -1); assertTrue(active.isEmpty());
    }
    @Test public void quantityOverflowDoesNotChangeTheDraft() {
        Cart cart = new Cart(); cart.add(pizza(), Collections.emptyMap(), 99);
        assertThrows(IllegalArgumentException.class, () -> cart.add(pizza(), Collections.emptyMap(), 1));
        assertThrows(IllegalArgumentException.class, () -> cart.change(cart.lines().get(0), 1));
        assertEquals(584100, cart.total());
    }
    @Test public void searchAcceptsCodesAndUnaccentedNames() {
        Cart.Item item = new Cart.Item("SP-046", "PÂTES AU POULET", "PÂTES", "Crème", 6500, Collections.emptyList());
        assertTrue(item.matches("pates")); assertTrue(item.matches("sp-046")); assertTrue(item.matches("creme")); assertFalse(item.matches("burger"));
    }
}
