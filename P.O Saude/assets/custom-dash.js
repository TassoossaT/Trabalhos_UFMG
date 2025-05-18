window.showTeamModal = function(facilityName) {
    // Store the clicked facility name
    window.clickedFacilityName = facilityName;
    
    // Trigger the modal display
    document.getElementById('team-detail-modal').style.display = 'block';
    
    // Send an event to the dash callback
    const event = new CustomEvent('facilitySelected', {
        detail: { facilityName: facilityName }
    });
    document.dispatchEvent(event);
    
    console.log('showTeamModal called for facility:', facilityName);
};
