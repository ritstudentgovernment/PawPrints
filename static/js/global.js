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
function getUrl(variable){
    try{
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i=0;i<vars.length;i++) {
            var pair = vars[i].split("=");
            if(pair[0] == variable){return pair[1];}
        }
        return(false);
    }
    catch(err){
        console.log("Error: " +err);
    }
}
$(document).ready(function(){
    var scrolledWaypoint = $("#sub-landing").waypoint(function(direction){
        if(direction == "down"){
            $("header").addClass("small-header header-scrolled");
        }
        else{
            $("header").removeClass("small-header header-scrolled");
        }
    }, {
        offset: '60px'
    });
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

(function( $ ){
    // Custom CSS animations plugin.
    $.fn.cssanimate = function( effect, options ){

        var element = $(this);
        var settings = $.extend({
            duration: 400,
            hide: true,
            inline: false
        }, options);

        function stripAnimationClasses(element){
            //This function strips all CSS Animation Classes from the given element.
            var classesToStrip = ["Animated","bounce","flash","pulse","rubberBand","shake","headShake","swing","tada","wobble","jello","bounceIn","bounceInDown","bounceInLeft","bounceInRight","bounceInUp","bounceOut","bounceOutDown","bounceOutLeft","bounceOutRight","bounceOutUp","fadeIn","fadeInDown","fadeInDownBig","fadeInLeft","fadeInLeftBig","fadeInRight","fadeInRightBig","fadeInUp","fadeInUpBig","fadeOut","fadeOutDown","fadeOutDownBig","fadeOutLeft","fadeOutLeftBig","fadeOutRight","fadeOutRightBig","fadeOutUp","fadeOutUpBig","flipInX","flipInY","flipOutX","flipOutY","lightSpeedIn","lightSpeedOut","rotateIn","rotateInDownLeft","rotateInDownRight","rotateInUpLeft","rotateInUpRight","rotateOut","rotateOutDownLeft","rotateOutDownRight","rotateOutUpLeft","rotateOutUpRight","hinge","rollIn","rollOut","zoomIn","zoomInDown","zoomInLeft","zoomInRight","zoomInUp","zoomOut","zoomOutDown","zoomOutLeft","zoomOutRight","zoomOutUp","slideInDown","slideInLeft","slideInRight","slideInUp","slideOutDown","slideOutLeft","slideOutRight","slideOutUp"];
            for(i=0;i<=classesToStrip.length;i++){
                if(element.hasClass(classesToStrip[i])){
                    element.removeClass(classesToStrip[i]);
                    console.log("Element '"+element+"' Had the class "+classesToStrip[i]+". It has been removed.");
                }
                else{
                    //console.log("Element '"+element+"' Does not have class "+classesToStrip[i]);
                }
            }
        }

        stripAnimationClasses(element);
        if(settings.hide){
            element.css({"display":"none"});
        }
        if(!settings.inline){
            element.css({"display":"block"});
        }
        else{
            element.css({"display":"inline-block"});
        }
        element.addClass("animated "+effect)

    }
    // Custom parallax element plugin.
    $.fn.parallax = function( options ){
        var selector = $(this);
        var position = selector.position();
        var settings = $.extend({
            offset:0,        // Integer to set the top position of the element.
            divisor:2.5,     // Integer used to set the ratio of the parallax effect
            class:'parallax' // The class to check for in children, if it doesn't exist, defaults are applied.
        },options);
        function initParallax(){
            if(!selector.hasClass(settings.class)){
                selector.css({
                    "transition":"all 0.05s linear",
                    "-moz-transition":"all 0.05s linear",
                    "-ms-transition":"all 0.05s linear",
                    "-o-transition":"all 0.05s linear",
                    "position":"absolute",
                    "top":settings.offset+"%",
                    "left":"0"
                });
            }
        }
        function updateParallax(){
            var scrollPos = window.pageYOffset || document.documentElement.scrollTop;
            // Only update the element's parallax position if it is currently visible
            if(inViewport(selector[0])){
                var newTop = ((position.top - scrollPos) / settings.divisor) + 1;
                selector.css({"transform":"translateY("+newTop+"px)"});
            }
            else{
                cancelAnimationFrame(parallaxAnimationFrame);
            }
        }
        window.addEventListener('scroll',function(){
            parallaxAnimationFrame = requestAnimationFrame(updateParallax);
        });
        initParallax();
    }
    // Custom slideshow plugin.
    $.fn.slideshow = function( options ){
        var selector = $(this);
        var settings = $.extend({
            slideClass:'slide',     // String:  The class of the slides in the slide show.
            slideDuration:5000,     // Integer: How long to display one slide. (ms)
            transition:'dissolve',  // String:  The transition to use. (only 'dissolve' currently)
            transitionDuration:500, // Integer: How long the transition takes. (ms)
            numSlides:0             // Integer: PRIVATE. The number of slides.
        },options)
        function setup(){
            selector.find('.'+settings.slideClass).each(function(){
                var me = $(this);
                console.log(me.data("backgroundimage"));
                var bg = "url('"+$(this).data("backgroundimage")+"')";
                console.log(bg);
                $(this).css({
                    "background-image":bg,
                    "background-size":"cover",
                    "background-position":"center",
                    "background-repeat":"no-repeat",
                    "position":"absolute",
                    "top:":0,
                    "left":0,
                    "opacity":0
                });
            });
            setTimeout(function(){
                switch(settings.transition){
                    case "dissolve":
                        selector.css({
                            "height":"100vh"
                        });
                        selector.find('.'+settings.slideClass).css({
                            "position":"absolute",
                            "top":0,
                            "left":0
                        });
                        var slide_num = 0;
                        selector.find('.'+settings.slideClass).each(function(){
                            var slide = $(this);
                            slide_num++;
                            if(slide_num > 1){
                                slide.css({"opacity":0});
                            }
                        });
                        settings.numSlides = slide_num;
                        break;
                    default:
                        console.log("Slide Show: Transition '"+settings.transition+"' was not found.");
                        break;
                }
                selector.find("."+settings.slideClass).css({
                    "transition":"all "+settings.transitionDuration+"ms linear",
                    "-moz-transition":"all "+settings.transitionDuration+"ms linear",
                    "-ms-transition":"all "+settings.transitionDuration+"ms linear",
                    "-o-transition":"all "+settings.transitionDuration+"ms linear",

                });
            },1);
        }
        current_slide = 0;
        function rotate(){
            if(inViewport(selector[0])){
                current_slide++;
                switch(settings.transition) {
                    case "dissolve":
                        var slide_selector = 0;
                        selector.find('.'+settings.slideClass).each(function(){
                            var slide = $(this);
                            slide_selector++;
                            if(current_slide < settings.numSlides){
                                if( slide_selector == current_slide ){
                                    // Fade out old slide
                                    slide.css({"opacity":0});
                                }
                                if( slide_selector == current_slide + 1){
                                    // Fade in the new slide
                                    slide.css({"opacity":1});
                                }
                            }
                        });
                        if(current_slide >= settings.numSlides){
                            var slide_num = 0;
                            selector.find('.'+settings.slideClass).each(function(){
                                var slide = $(this);
                                slide_num++;
                                if(slide_num > 1){
                                    slide.css({"opacity":0});
                                }
                                else{
                                    slide.css({"opacity":1});
                                }
                            });
                            current_slide = 0;
                        }
                        break;
                    default:
                        break;
                }
            }
            setTimeout(function(){rotate();},settings.slideDuration);
        }
        setup();
        rotate();
    }
}( jQuery ));
// requestAnimationFrame polyfill by Erik Miller. fixes from Paul Irish and Tino Zijdel
// MIT license
// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
// http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
!function(){for(var a=0,b=["ms","moz","webkit","o"],c=0;c<b.length&&!window.requestAnimationFrame;++c)window.requestAnimationFrame=window[b[c]+"RequestAnimationFrame"],window.cancelAnimationFrame=window[b[c]+"CancelAnimationFrame"]||window[b[c]+"CancelRequestAnimationFrame"];window.requestAnimationFrame||(window.requestAnimationFrame=function(b,c){var d=(new Date).getTime(),e=Math.max(0,16-(d-a)),f=window.setTimeout(function(){b(d+e)},e);return a=d+e,f}),window.cancelAnimationFrame||(window.cancelAnimationFrame=function(a){clearTimeout(a)})}();