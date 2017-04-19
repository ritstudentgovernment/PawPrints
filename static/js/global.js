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
    // Custom Modal Plugin
    // Relies on jQuery, animate.css and my custom cssanimate jQuery plugin.
    function buildModal(){
        // Constructs a new modal from the modal template and configures it based on user settings.

        if(this.settings.debug){
            console.log(this);
        }

        if(this.settings.clone) {
            this.element = $("#modal-template").find(".modal").clone();
        }
        else{
            this.element = $("#modal-template").find(".modal");
        }

        if(this.settings.exitButton){

            this.exitButton = this.element.find(".modal-close-button");
            this.exitButton.removeClass("hidden");
            this.exitButton = this.exitButton[0];

        }
        if(this.settings.overlay){

            this.overlay = this.element.find(".modal-overlay");
            this.overlay.removeClass("hidden");
            this.overlay = this.overlay[0];

        }

        if(this.settings.icon){

            this.element.find(".material-icon-container").addClass(this.settings.iconContainerClass).removeClass("hidden");
            this.element.find(".material-icons").html(this.settings.iconText);

        }

        this.element.find(".modal-header").addClass(this.settings.headerClass);
        if(this.settings.headerContent){
            this.element.find(".modal-header-content").html(this.settings.headerContent);
        }

        var me = this;
        this.element.find(".modal-body").addClass(this.settings.bodyClass);
        if(this.settings.bodyContent){
            this.element.find(".modal-content").html(this.settings.bodyContent);
        }

        if(this.settings.bodyButtons){

            var buttonsContainer = this.element.find(".modal-buttons").removeClass("hidden");

            for(bid in this.settings.bodyButtons){
                var button = this.settings.bodyButtons[bid];
                buttonsContainer.append("<button class='"+button[1]+"' onclick='"+button[2]+"'>"+button[0]+"</button>");
            }

        }

        if(this.settings.clone){
            $("body").append(me.element);
        }
        else{
            me.element.css("display","block");
        }

        me.element.removeClass("hidden");

        setTimeout(function(){
            var elementHeight = $(me.element).find(".modal-container").height();
            var windowHeight = $(window).height();
            var topOffset = (windowHeight / 2) - (elementHeight / 2);
            topOffset = topOffset > 0 ? topOffset : 0;
            me.element.find(".modal-container").css({"top":topOffset+"px"});

        },0);
        $(window).resize(function(){
            var elementHeight = $(me.element).find(".modal-container").height();
            var windowHeight = $(window).height();
            var topOffset = (windowHeight / 2) - (elementHeight / 2);
            topOffset = topOffset > 0 ? topOffset : 0;
            me.element.find(".modal-container").css({"top":topOffset+"px"});
        });

        if(this.settings.debug){
            console.log(this);
        }

        return this;

    }
    function bindModalEvents(){
        // Function that binds the exit events to the modal.
        if(this.settings.exitButton){
            this.exitButton.addEventListener('click', this.close.bind(this));
        }
        if(this.settings.overlay && this.settings.exitOverlayOnClick){
            this.overlay.addEventListener('click', this.close.bind(this));
        }

        if(this.settings.debug){
            console.log(this);
        }

        return this;

    }
    function unbindModalEvents() {
        // Function that unbinds the exit events from the modal.
        if (this.exitButton) {
            this.exitButton.removeEventListener('click');
        }
        if (this.settings.overlay && this.settings.exitOverlayOnClick) {
            this.overlay.removeEventListener('click');
        }

        if(this.settings.debug){
            console.log(this);
        }

        return this;

    }

    this.Modal = function(options){
        // Requirements:
        //     - Overlay:                 On/Off
        //     - Exit Button:             On/Off
        //     - Exit on overlay click:   On/Off
        //     - Material Icon Container: On/Off + Class Selection
        //     - Material Icon:           Content Replace
        //     - Header Content:          Content Replace + Class Selection
        //     - Body:                    Class Selection
        //     - Body Content:            Content Replace
        //     - Body Buttons (wrapper):  On/Off + Class Selection
        //     - Body Buttons:            Content Replace + Class Selection + Click Action.
        this.element = null;
        this.exitButton = null;
        this.overlay = null;

        this.settings = $.extend({
            exitButton: true,
            overlay: true,
            exitOverlayOnClick: true,
            inAnimation: "fadeInUp",
            outAnimation: "fadeOutDown",
            animationDuration: 400,
            icon: true,
            iconContainerClass: " circle green-border green-text",
            iconText: "check",
            headerContent: "<h2>Great Work!</h2><p>All Tests Have Passed!</p>",
            headerClass: "",
            bodyClass: "padding highlight",
            bodyContent: null,
            bodyButtons: [["Next Section", "modern-button margin-bottom margin-top transition cursor",function(){}]],
            closeCallback: function(){},
            debug: false,
            clone: true
        },options);

        return this;

    }
    Modal.prototype.open = function(){

        var me = this;

        buildModal.call(me);
        bindModalEvents.call(me);

        if(me.overlay){
            $(me.overlay).fadeIn(me.settings.animationDuration);
        }
        me.element.find(".modal-container").cssanimate(me.settings.inAnimation,{duration: me.settings.animationDuration});

    };
    Modal.prototype.close = function(){

        unbindModalEvents.call(this);
        if(this.overlay){
            $(this.overlay).fadeOut(this.settings.animationDuration);
        }

        var me = this;

        me.element.find(".modal-container").cssanimate(this.settings.outAnimation,{duration: this.settings.animationDuration * 2},function(){
            if(me.settings.clone){
                me.element.remove();
            }
            else{
                me.element.css("display","none");
            }
        });

        setTimeout(function(){
            me.settings.closeCallback();
        },this.settings.animationDuration);

    };
    // Custom CSS animations plugin.
    $.fn.cssanimate = function( effect, options, callback ){

        var element = $(this);
        var settings = $.extend({
            duration: 400,
            hide: true,
            inline: false
        }, options);

        if(typeof callback != "function"){
            callback = function(){};
        }

        function stripAnimationClasses(){
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

        function addDelays(){
            element.css({
                "-webkit-transition-duration":settings.duration+"ms",
                "transition-duration":settings.duration+"ms"
            });
        }

        stripAnimationClasses();
        addDelays();

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

        setTimeout(function(){
            callback();
        },settings.duration * 2);

        return element;

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
            numSlides:0,            // Integer: PRIVATE. The number of slides.
            debug: false
        },options);
        function setup(){
            selector.find('.'+settings.slideClass).each(function(){
                var me = $(this);
                if(settings.debug){
                    console.log(me.data("backgroundimage"));
                }
                var bg = "url('"+$(this).data("backgroundimage")+"')";
                if(settings.debug){
                    console.log(bg);
                }
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
        function countDecimalPlaces(num) {
            var match = (''+num).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
            if (!match) { return 0; }
            return Math.max(
                0,
                // Number of digits right of decimal point.
                (match[1] ? match[1].length : 0)
                // Adjust for scientific notation.
                - (match[2] ? +match[2] : 0));
        }
        function roundToNumDecimalPlaces(num, decimalPlaces){
            return +(num.toFixed(decimalPlaces));
        }
        function breathe(start, end, step, current = start, reverse = false){

            var delay = settings.transitionDuration;
            if( (start <= current) && (current < end) && !reverse){

                current += step;
                current = roundToNumDecimalPlaces(current, countDecimalPlaces(step));
                setTimeout(function(){
                    breathe(start,end,step,current);
                },delay);

            }
            else {

                current -= step;
                current = roundToNumDecimalPlaces(current, countDecimalPlaces(step));
                setTimeout(function(){
                    if(current == start){
                        breathe(start,end,step);
                    }
                    else{
                        breathe(start, end, step, current, true);
                    }
                },delay);

            }

            $("."+settings.slideClass).css("transform","scale("+current+")");

        }
        setup();
        rotate();
        breathe(1,1.1,0.002);
    }
}( jQuery ));

// requestAnimationFrame polyfill by Erik Miller. fixes from Paul Irish and Tino Zijdel
// MIT license
// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
// http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
!function(){for(var a=0,b=["ms","moz","webkit","o"],c=0;c<b.length&&!window.requestAnimationFrame;++c)window.requestAnimationFrame=window[b[c]+"RequestAnimationFrame"],window.cancelAnimationFrame=window[b[c]+"CancelAnimationFrame"]||window[b[c]+"CancelRequestAnimationFrame"];window.requestAnimationFrame||(window.requestAnimationFrame=function(b,c){var d=(new Date).getTime(),e=Math.max(0,16-(d-a)),f=window.setTimeout(function(){b(d+e)},e);return a=d+e,f}),window.cancelAnimationFrame||(window.cancelAnimationFrame=function(a){clearTimeout(a)})}();
