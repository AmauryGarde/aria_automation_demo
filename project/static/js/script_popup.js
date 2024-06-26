document.addEventListener("DOMContentLoaded", function() {
    const addBtn = document.getElementById("add-btn");
    const closeBtn = document.getElementById("productCloseButton");
    const modalBg = document.querySelector(".bg-modal");

    const productNameInput = document.getElementById("productNameId");
    const productPriceInput = document.getElementById("productPriceId");
    const productSaveButton = document.getElementById("productSaveButton");

    let isEditing = false;
    let currentId = null;

    productNameInput.addEventListener("input", validateInputs);
    productPriceInput.addEventListener("input", validateInputs);

    function validateInputs() {
        const productNameValue = productNameInput.value.trim();
        const productPriceValue = productPriceInput.value.trim();

        const isPriceValid = /^\d+(\.\d{1,2})?$/.test(productPriceValue);

        if (productNameValue !== "" && isPriceValid) {
            productSaveButton.removeAttribute("disabled");
        } else {
            productSaveButton.setAttribute("disabled", true);
        }
    }

    closeBtn.addEventListener("click", function() {
        modalBg.style.display = 'none';
        productNameInput.value = ''; // Clear the product name input field
        productPriceInput.value = ''; // Clear the product price input field
        productSaveButton.setAttribute("disabled", true); // Disable the "Add" button
        isEditing = false;
        currentId = null;
    });

    addBtn.addEventListener("click", function() {
        modalBg.style.display = 'flex';
    });

    productSaveButton.addEventListener("click", function() {
        const name = productNameInput.value;
        const price = productPriceInput.value;

        if (isEditing) {
            // Perform an update
            fetch('/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'name': name,
                    'price': price,
                    'id': currentId
                })
            }).then(response => {
                // Redirect to home or refresh the page
                location.reload();
            });
        } else {
            // Perform a create
            fetch('/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'name': name,
                    'price': price
                })
            }).then(response => {
                // Redirect to home or refresh the page
                location.reload();
            });
        }
    });

    // Get the edit buttons
    const editButtons = document.querySelectorAll(".edit-btn");

    // Add click event listener to each edit button
    editButtons.forEach(function(editButton) {
        editButton.addEventListener("click", function() {
            const id = editButton.getAttribute("data-id");
            const name = editButton.getAttribute("data-name");
            const price = editButton.getAttribute("data-price");

            // Set the flag to indicate that we are editing
            isEditing = true;
            currentId = id;

            // Populate the modal with the row data
            productNameInput.value = name;
            productPriceInput.value = price;

            // Show the modal
            modalBg.style.display = "flex";
        });
    });

});
