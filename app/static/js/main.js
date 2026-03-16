/* File path: app/static/js/main.js */

console.log("Meal Tracker loaded.");

document.addEventListener("DOMContentLoaded", () => {
    const addRowBtn = document.getElementById("add-saved-meal-row-btn");
    const removeRowBtn = document.getElementById("remove-saved-meal-row-btn");
    const tableBody = document.getElementById("saved-meal-items-body");

    if (!addRowBtn || !removeRowBtn || !tableBody) {
        return;
    }

    const foods = Array.isArray(window.savedMealFoods) ? window.savedMealFoods : [];
    const units = Array.isArray(window.savedMealUnits) ? window.savedMealUnits : [];

    function buildFoodOptions() {
        const base = ['<option value="">-- Select Food --</option>'];
        foods.forEach((food) => {
            base.push(`<option value="${food.id}">${food.label}</option>`);
        });
        return base.join("");
    }

    function buildUnitOptions() {
        const base = ['<option value="">-- Select Unit --</option>'];
        units.forEach((unit) => {
            base.push(`<option value="${unit.value}">${unit.label}</option>`);
        });
        return base.join("");
    }

    function addRow() {
        const tr = document.createElement("tr");
        tr.className = "saved-meal-item-row";
        tr.innerHTML = `
            <td>
                <select name="food_id">
                    ${buildFoodOptions()}
                </select>
            </td>
            <td>
                <input type="number" step="any" name="amount">
            </td>
            <td>
                <select name="unit">
                    ${buildUnitOptions()}
                </select>
            </td>
        `;
        tableBody.appendChild(tr);
    }

    function removeRow() {
        const rows = tableBody.querySelectorAll(".saved-meal-item-row");
        if (rows.length <= 1) {
            return;
        }
        rows[rows.length - 1].remove();
    }

    addRowBtn.addEventListener("click", addRow);
    removeRowBtn.addEventListener("click", removeRow);
    
    const addOptionalRowBtn = document.getElementById("add-saved-meal-optional-row-btn");
    const removeOptionalRowBtn = document.getElementById("remove-saved-meal-optional-row-btn");
    const optionalTableBody = document.getElementById("saved-meal-optional-items-body");

    function buildOptionalFoodOptions() {
        const base = ['<option value="">-- Select Optional Food --</option>'];
        foods.forEach((food) => {
            base.push(`<option value="${food.id}">${food.label}</option>`);
        });
        return base.join("");
    }

    function addOptionalRow() {
        if (!optionalTableBody) return;

        const tr = document.createElement("tr");
        tr.className = "saved-meal-optional-item-row";
        tr.innerHTML = `
            <td>
                <select name="optional_food_id">
                    ${buildOptionalFoodOptions()}
                </select>
            </td>
        `;
        optionalTableBody.appendChild(tr);
    }

    function removeOptionalRow() {
        if (!optionalTableBody) return;

        const rows = optionalTableBody.querySelectorAll(".saved-meal-optional-item-row");
        if (rows.length <= 1) {
            return;
        }
        rows[rows.length - 1].remove();
    }

    if (addOptionalRowBtn) {
        addOptionalRowBtn.addEventListener("click", addOptionalRow);
    }

    if (removeOptionalRowBtn) {
        removeOptionalRowBtn.addEventListener("click", removeOptionalRow);
    }
});
