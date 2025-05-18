// This is a custom JavaScript file to help with marker interactions

// Function to handle facility marker clicks and show team data
window.showTeamData = function(facilityName) {
    // Log that the function was called
    console.log("showTeamData called for:", facilityName);
    
    // Set the clicked facility name in a global variable
    window.clickedFacilityName = facilityName;
    
    // Find the modal element
    var modal = document.getElementById('team-detail-modal');
    if (modal) {
        // Display the modal
        modal.style.display = 'block';
    }
};

// Close the modal when clicking the X button
document.addEventListener('DOMContentLoaded', function() {
    var closeBtn = document.getElementById('close-team-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            var modal = document.getElementById('team-detail-modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        var modal = document.getElementById('team-detail-modal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
});
