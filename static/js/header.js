function openDropdown(id) {
    // console.log(document.getElementById(id));
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (i = 0; i != dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
        document.getElementById("myDropdown"+id).classList.toggle("show");
    }
    
    
function closeDropdown(id) {
    //console.log(document.getElementById(id)+"close");
    document.getElementById("myDropdown"+id).classList.remove("show");
    
} 

 window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i != dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}