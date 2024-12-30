function openTab(tabName) {
    // Hide all tab contents by removing the 'active' class
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Deactivate all tab buttons by removing the 'active' class
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show the content of the selected tab by adding the 'active' class
    document.getElementById(tabName).classList.add('active');
    
    // Activate the button for the selected tab by adding the 'active' class
    event.currentTarget.classList.add('active');
}
