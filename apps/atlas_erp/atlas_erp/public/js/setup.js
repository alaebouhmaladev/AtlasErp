"use strict";
(() => {
  const $ = id => document.getElementById(id);
  let data = null;
  let loading = false;
  const notify = (message, error = false) => {
    $("notice").textContent = message;
    $("notice").classList.toggle("error", error);
  };
  async function call(method, payload) {
    const response = await fetch(`/api/method/atlas_erp.business_setup.${method}`, {
      method: payload ? "POST" : "GET",
      credentials: "same-origin",
      headers: payload ? {"Content-Type": "application/json", "X-Frappe-CSRF-Token": document.querySelector('meta[name="csrf-token"]').content} : {},
      body: payload ? JSON.stringify(payload) : undefined
    });
    const body = await response.json();
    if (!response.ok || body.exc) {
      let message = "Could not save this change. Check your access and the entered details.";
      try {
        const messages = JSON.parse(body._server_messages || "[]");
        if (messages.length) message = JSON.parse(messages[0]).message;
      } catch (_) { /* Keep the safe fallback. */ }
      // Frappe validation messages can contain HTML. Show their text only.
      const parser = new DOMParser().parseFromString(message, "text/html");
      throw new Error(parser.body.textContent);
    }
    return body.message;
  }
  function option(select, value, title) {
    const node = document.createElement("option");
    node.value = value;
    node.textContent = title;
    select.append(node);
  }
  function options(id, rows, label, selected) {
    const select = $(id);
    select.replaceChildren();
    option(select, "", "Choose…");
    rows.forEach(row => option(select, row.name, row[label]));
    if (rows.some(row => row.name === selected)) select.value = selected;
    else if (rows.length === 1) select.value = rows[0].name;
  }
  function recordList(id, rows, title, subtitle, doctype) {
    const list = $(id);
    list.replaceChildren();
    rows.forEach(row => {
      const li = document.createElement("li");
      const text = document.createElement("div");
      text.textContent = row[title];
      const small = document.createElement("small");
      small.textContent = subtitle(row);
      text.append(small);
      const link = document.createElement("a");
      link.href = `/desk/${doctype}/${encodeURIComponent(row.name)}`;
      link.textContent = "Open ↗";
      li.append(text, link);
      list.append(li);
    });
    if (!rows.length) {
      const li = document.createElement("li");
      li.textContent = "Nothing added yet.";
      list.append(li);
    }
  }
  function render() {
    const company = $("company").value;
    const manageable = data.managed_companies.includes(company);
    const selected = data.companies.find(c => c.name === company);
    $("company-details").textContent = selected ? `${selected.country} · ${selected.default_currency}` : "Select a company to continue.";
    $("company-admin").hidden = !data.is_admin;
    const brands = data.brands.filter(b => b.company === company);
    const branches = data.branches.filter(b => b.company === company);
    const team = data.team.filter(t => t.company === company);
    options("branch-brand", brands.filter(b => !b.disabled), "brand_name", $("branch-brand").value);
    options("team-branch", branches.filter(b => !b.disabled), "branch_name", $("team-branch").value);
    for (const id of ["brand-form", "branch-form", "team-form"]) {
      $(id).hidden = !manageable;
      $(id).querySelectorAll("button").forEach(b => b.disabled = loading || !company);
    }
    recordList("brands", brands, "brand_name", b => `${b.business_type}${b.disabled ? " · Disabled" : ""}`, "atlas-business-brand");
    recordList("branches", branches, "branch_name", b => `${b.code} · ${b.city || "City not set"} · ${b.warehouse}`, "atlas-business-branch");
    $("team").replaceChildren();
    team.forEach(member => {
      const row = document.createElement("tr");
      const branch = branches.find(b => b.name === member.branch);
      for (const value of [member.user, branch?.branch_name || member.branch, member.staff_role, member.enabled ? "Enabled" : "Disabled"]) {
        const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
      }
      const action = document.createElement("td");
      if (manageable) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = member.enabled ? "Disable" : "Enable";
        button.addEventListener("click", () => mutate(button, "set_staff_enabled", {name: member.name, enabled: member.enabled ? 0 : 1}, "Staff access updated."));
        action.append(button);
      }
      row.append(action); $("team").append(row);
    });
    if (!manageable && selected) notify("You are viewing your assigned business access. Ask your owner to change setup.");
  }
  async function refresh(keepNotice = false) {
    try {
      const selected = $("company").value;
      data = await call("overview");
      options("company", data.companies, "name", selected);
      render();
      if (!keepNotice) notify(data.companies.length ? "Your saved setup is ready to continue." : "Create a legal company, then refresh this page.");
    } catch (error) { notify(error.message, true); }
  }
  async function mutate(button, method, payload, message) {
    if (loading) return;
    loading = true; button.disabled = true;
    notify("Saving…");
    try {
      const result = await call(method, payload);
      await refresh(true);
      notify(result.activation || (result.created === false ? "Existing record found. No duplicate was created." : message));
    } catch (error) { notify(error.message, true); }
    finally { loading = false; button.disabled = false; if (data) render(); }
  }
  for (const [id, method, message] of [["brand-form", "save_brand", "Brand saved."], ["branch-form", "save_branch", "Branch and warehouse saved."], ["team-form", "assign_staff", "Staff access saved."]]) {
    $(id).addEventListener("submit", event => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(event.target));
      if (id !== "team-form") payload.company = $("company").value;
      mutate(event.target.querySelector("button"), method, payload, message);
    });
  }
  $("company").addEventListener("change", render);
  $("refresh").addEventListener("click", () => refresh());
  refresh();
})();
