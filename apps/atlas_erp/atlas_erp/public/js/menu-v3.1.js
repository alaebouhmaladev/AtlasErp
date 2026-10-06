// Accessible client-only filtering; no authentication, orders or ERP writes.
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('menu-search');
    const groups = [...document.querySelectorAll('.menu-category')];
    const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
    const entries = groups.map(group => ({group, cards: [...group.querySelectorAll('.menu-card')].map(card => ({card, text: normalize(card.textContent)}))}));
    input.addEventListener('input', () => {
        const query = normalize(input.value.trim());
        let count = 0;
        entries.forEach(({group, cards}) => {
            let visible = 0;
            cards.forEach(({card, text}) => {card.hidden = !text.includes(query); if (!card.hidden) visible++;});
            group.hidden = !visible;
            count += visible;
        });
        document.getElementById('menu-result').textContent = query ? `${count} / ${entries.reduce((sum, group) => sum + group.cards.length, 0)}` : '';
    });
});
