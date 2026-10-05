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
