// Display labels only: persisted module names and document identifiers stay intact.
const applyAtlasLabels = () => {
    frappe._messages = frappe._messages || {};
    frappe._messages["ERPNext Integrations"] = __("Business integrations");
    frappe._messages["ERPNext Settings"] = __("ATLASERP Settings");
    frappe._messages["ERPNext User ID"] = __("ATLASERP User ID");
};
// Register before DOM-ready startup awaits the same translation promise.
Promise.resolve(frappe._translations_loaded).then(applyAtlasLabels);

$(document).ready(() => {
    const brand = frappe.boot && frappe.boot.atlas_brand;
    if (!brand) return;
    const updateTitle = () => {
        // Keep the current task in the browser title, replacing product suffixes only.
        document.title = document.title.replace(/\b(?:ERPNext|Frappe Framework)\b/g, brand.name);
    };
    updateTitle();
    if (frappe.router) frappe.router.on("change", updateTitle);
});

// Add one product-home shortcut to the native sidebar without rebuilding its
// permission-filtered navigation. Reconcile only when the sidebar is replaced.
$(document).ready(() => {
    const addHome = () => {
        document.querySelectorAll('.body-sidebar').forEach(sidebar => {
            if (sidebar.querySelector('.atlas-workspace-link')) return;
            const link = document.createElement('a');
            link.className = 'atlas-workspace-link';
            link.href = '/atlas';
            const mark = document.createElement('img');
            mark.src = '/assets/atlas_erp/images/atlas-mark.svg';
            mark.alt = '';
            const label = document.createElement('span');
            label.textContent = __('Business workspace');
            link.append(mark, label);
            sidebar.prepend(link);
        });
    };
    addHome();
    if (frappe.router) frappe.router.on('change', addHome);
    // Desk creates/replaces the sidebar after asynchronous startup.
    const observer = new MutationObserver(records => {
        if (records.some(record => [...record.addedNodes].some(node =>
            node.nodeType === 1 && (node.matches('.body-sidebar') || node.querySelector('.body-sidebar'))
        ))) addHome();
    });
    observer.observe(document.body, {childList: true, subtree: true});
});
