/**
 * File: global.js
 * Desc: This file houses functions that will be commonly used throughout the PawPrints site.
 * Auth: Lukas Yelle (lxy5611)
 * Date: 10/17/16.
 * Lang: JavaScript
 */

function getCookie(cname) {
    /*
    * This function was created by W3Schools.
    * It's purpose is to get a specified cookie's value.
    * */
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}
function get_csrf(){
    /*
    * This function returns the CSRF token for easier future use.
    * */
    return getCookie('csrftoken');
}
$(document).ready(function(){
    $(".create_petition").click(function(){
        $.post('/petition/create/',{"csrfmiddlewaretoken":get_csrf()},function(response){
            window.location.href = "/petition/"+response;
        });
    });
});
function inViewport (el) {

    var r, html;
    if ( !el || 1 !== el.nodeType ) { return false; }
    html = document.documentElement;

    r = el.getBoundingClientRect();

    return ( !!r
        && r.bottom >= 0
        && r.right >= 0
        && r.top <= html.clientHeight
        && r.left <= html.clientWidth
    );

}