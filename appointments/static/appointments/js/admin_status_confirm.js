document.addEventListener('DOMContentLoaded', function() {
    // List view selectors (formset) and detail view selector (status)
    const selectors = [
        'select[name^="form-"][name$="-status"]', // List view
        'select[name="status"]'                   // Detail view
    ];

    selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(function(select) {
            // Store the initial value to revert if cancelled
            select.dataset.previousValue = select.value;

            select.addEventListener('change', function(event) {
                const newValue = event.target.value;
                const oldValue = event.target.dataset.previousValue;

                // Check if the new value is 'completed' or 'cancelled'
                if (newValue === 'completed' || newValue === 'cancelled') {
                    const actionName = newValue.charAt(0).toUpperCase() + newValue.slice(1);
                    const confirmed = confirm(`Are you sure you want to change this appointment status to ${actionName}? Click OK to Confirm or Cancel to revert.`);

                    if (!confirmed) {
                        // Revert to old value
                        event.target.value = oldValue;
                        return false;
                    }
                }

                // Update the previous value tracker
                event.target.dataset.previousValue = newValue;
            });
        });
    });
});
