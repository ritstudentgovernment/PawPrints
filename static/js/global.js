/**
 * File: global.js
 * Desc: This file houses functions that will be commonly used throughout the PawPrints site.
 * Auth: Lukas Yelle (lxy5611)
 * Date: 10/17/16.
 * Lang: JavaScript
 **/

function getCookie(cname) {
    /**
    * This function was created by W3Schools.
    * It's purpose is to get a specified cookie's value.
    **/

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
    /**
    * This function returns the CSRF token for easier future use.
    **/
    return getCookie('csrftoken');
}


function getUrl(variable){
    /**
     * This function returns a given URL variable's value if it exists, false otherwise.
     **/
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

function scroll(to_elem){
    /**
     * This function smoothly scrolls the viewport to a given element.
     **/
    var offset = to_elem.offset().top;
    var fsh = $("#filter-sort").height();
    if(fsh < 300) offset -= fsh - 7;
    offset -= $("header").height() + $("nav").find(".header-top").height() - 1;
    $('html, body').stop().animate({'scrollTop': offset+"px"}, 700);
}

function verticalOffset(element, givenOffset = false){
    /**
     * This function is responsible for positioning (via top property) an element in the center of its
     * parent.
     **/
    var elementHeight = element.height();
    var windowHeight = $(window).height();
    var topOffset = (windowHeight / 2) - (elementHeight / 2);
    topOffset = topOffset > 0 ? topOffset : 0;          // Prevent negative values.
    topOffset = !givenOffset ? topOffset : givenOffset; // Provide a offset override.
    console.log(elementHeight + " | " + windowHeight + " = "+ topOffset);
    element.css({"top":topOffset+"px"});
}

$(document).ready(function(){
    $(".create_petition").click(function(){
        $.post('/petition/create/',{"csrfmiddlewaretoken":get_csrf()},function(response){
            window.location.href = "/petition/"+response;
        });
    });
    var $mobile = $("#mobile-nav").mmenu({
        offCanvas: {
            position: "right",
            pageSelector: "#wrapper"
        },
        navbar: {
            title:"PawPrints"
        },
        extensions: [
            "pagedim-black"
        ]
    });
    $().smartWebBanner({
        title: 'PawPrints',
        author: 'RIT Student Government',
        url: '/',
        autoApp: true
    });
    var $icon = $("#menu-icon");
    var API = $mobile.data( "mmenu" );
    $icon.on( "click", function() {
        if(!$(this).hasClass("is-active"))API.open();
        else API.close();
    });
    API.bind( "open:start", function() {
        $icon.addClass( "is-active" );
        $("#wrapper").click(function(){
            API.close();
            $("#wrapper").unbind("click");
        });
        var resize = $(window).resize(function(){
            API.close();
            resize = null;
        });
    });
    API.bind( "close:start", function() {
        $icon.removeClass( "is-active" );
    });
    var scrolledWaypoint = $("#sub-landing").waypoint(function(direction){
        if(direction == "down"){
            $("header").addClass("small-header header-scrolled");
            $("#back-up").stop().fadeIn(100);
            $(".attach").each(function(){
                var me = $(this);
                var topPos = me.data("top");
                var leftPos = me.data("left");
                var rightPos = me.data("right");
                var bottomPos = me.data("bottom");
                me.addClass("attached");
                if(topPos !== undefined){
                    me.css({"top":topPos+"px"});
                }
                if(leftPos !== undefined){
                    me.css({"left":leftPos+"px"});
                }
                if(rightPos !== undefined){
                    me.css({"right":rightPos+"px"});
                }
                if(bottomPos !== undefined){
                    me.css({"bottom":bottomPos+"px"});
                }
            });
        }
        else{
            $("header").removeClass("small-header header-scrolled");
            $("#back-up").stop().fadeOut(200);
            $(".attach").each(function(){
                var me = $(this);
                var topPos = me.data("top");
                var leftPos = me.data("left");
                var rightPos = me.data("right");
                var bottomPos = me.data("bottom");
                me.removeClass("attached");
                if(topPos !== undefined){
                    me.css({"top":""});
                }
                if(leftPos !== undefined){
                    me.css({"left":""});
                }
                if(rightPos !== undefined){
                    me.css({"right":""});
                }
                if(bottomPos !== undefined){
                    me.css({"bottom":""});
                }
            });
        }
    }, {
        offset: '60px'
    });
    $("#back-up").click(function(e){
        e.preventDefault();
        var to_elem = $("#landing-marker");
        scroll(to_elem);
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

function checkErrorInResponse(response,callback=false){
    try{
        if(response.hasOwnProperty("Error")){
            window.errorModal = new Modal({
                iconText:"error",
                iconClass:"bright-text md-48",
                iconContainerClass:"",
                headerClass:"error-background bright-text",
                headerContent: "<h2>Error</h2>",
                bodyContent:"<p>"+response.Error+"</p>",
                bodyButtons:[
                    ["OK","material-button material-hover material-shadow cursor transition minimal","window.errorModal.close()"]
                ]
            });
            errorModal.open();
        }
        else{
            if(callback && typeof callback === "function"){
                callback(response);
            }
        }
    }
    catch(e){
        console.log("Error: "+ e + "\nResponse: " + response);
    }
}

function publishPetition(petition){
    $.post("/petition/update/"+petition,{"attribute":"publish","value":"none","csrfmiddlewaretoken":get_csrf()},function(r){
        checkErrorInResponse(r,function(){
            window.location.href="/?p="+petition;
        });
    });
}

function update(what, value, petition_id, callback=false){
    $.post("/petition/update/"+petition_id,{"attribute":what,"value":value,"csrfmiddlewaretoken":get_csrf()},function(r){
        checkErrorInResponse(r,callback);
    });
}

function ucfirst(string){
    return string.charAt(0).toUpperCase() + string.substr(1);
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
            this.element.find(".material-icons").addClass(this.settings.iconClass).html(this.settings.iconText);

        }
        else{

            this.element.find(".material-icon-container").remove();
            this.element.find(".modal-header").removeClass("padding-top");

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
            this.exitButton.removeEventListener('click', this.close.bind(this));
        }
        if (this.settings.overlay && this.settings.exitOverlayOnClick) {
            this.overlay.removeEventListener('click', this.close.bind(this));
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
            iconClass:"",
            iconText: "check",
            headerContent: "<h2>Great Work!</h2><p>All Tests Have Passed!</p>",
            headerClass: "",
            bodyClass: "padding highlight",
            bodyContent: null,
            bodyButtons: [["Next Section", "modern-button margin-bottom margin-top transition cursor",function(){}]],
            closeCallback: function(){},
            debug: true,
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
        element.addClass("animated "+effect);

        setTimeout(function(){
            callback();
        },settings.duration * 2);

        return element;

    };
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
                    "-o-transition":"all "+settings.transitionDuration+"ms linear"
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

;(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else if (typeof exports === 'object') {
        module.exports = factory(require('jquery'));
    } else {
        root.jquery_mmenu_min_js = factory(root.jQuery);
    }
}(this, function(jQuery) {
    /*
     * jQuery mmenu v6.0.2
     * @requires jQuery 1.7.0 or later
     *
     * mmenu.frebsite.nl
     *
     * Copyright (c) Fred Heusschen
     * www.frebsite.nl
     *
     * License: CC-BY-NC-4.0
     * http://creativecommons.org/licenses/by-nc/4.0/
     */
    !function(t){function e(){t[n].glbl||(o={$wndw:t(window),$docu:t(document),$html:t("html"),$body:t("body")},s={},a={},r={},t.each([s,a,r],function(t,e){e.add=function(t){t=t.split(" ");for(var n=0,i=t.length;n<i;n++)e[t[n]]=e.mm(t[n])}}),s.mm=function(t){return"mm-"+t},s.add("wrapper menu panels panel nopanel highest opened subopened navbar hasnavbar title btn prev next listview nolistview inset vertical selected divider spacer hidden fullsubopen noanimation"),s.umm=function(t){return"mm-"==t.slice(0,3)&&(t=t.slice(3)),t},a.mm=function(t){return"mm-"+t},a.add("parent child"),r.mm=function(t){return t+".mm"},r.add("transitionend webkitTransitionEnd click scroll resize keydown mousedown mouseup touchstart touchmove touchend orientationchange"),t[n]._c=s,t[n]._d=a,t[n]._e=r,t[n].glbl=o)}var n="mmenu",i="6.0.2";if(!(t[n]&&t[n].version>i)){t[n]=function(t,e,n){return this.$menu=t,this._api=["bind","getInstance","initPanels","openPanel","closePanel","closeAllPanels","setSelected"],this.opts=e,this.conf=n,this.vars={},this.cbck={},this.mtch={},"function"==typeof this.___deprecated&&this.___deprecated(),this._initAddons(),this._initExtensions(),this._initMenu(),this._initPanels(),this._initOpened(),this._initAnchors(),this._initMatchMedia(),"function"==typeof this.___debug&&this.___debug(),this},t[n].version=i,t[n].addons={},t[n].uniqueId=0,t[n].defaults={extensions:[],initMenu:function(){},initPanels:function(){},navbar:{add:!0,title:"Menu",titleLink:"parent"},onClick:{setSelected:!0},slidingSubmenus:!0},t[n].configuration={classNames:{divider:"Divider",inset:"Inset",nolistview:"NoListview",nopanel:"NoPanel",panel:"Panel",selected:"Selected",spacer:"Spacer",vertical:"Vertical"},clone:!1,openingInterval:25,panelNodetype:"ul, ol, div",transitionDuration:400},t[n].prototype={getInstance:function(){return this},initPanels:function(t){this._initPanels(t)},openPanel:function(e,i){if(this.trigger("openPanel:before",e),e&&e.length&&(e.is("."+s.panel)||(e=e.closest("."+s.panel)),e.is("."+s.panel))){var r=this;if("boolean"!=typeof i&&(i=!0),e.hasClass(s.vertical))e.add(e.parents("."+s.vertical)).removeClass(s.hidden).parent("li").addClass(s.opened),this.openPanel(e.parents("."+s.panel).not("."+s.vertical).first()),this.trigger("openPanel:start",e),this.trigger("openPanel:finish",e);else{if(e.hasClass(s.opened))return;var o=this.$pnls.children("."+s.panel),l=o.filter("."+s.opened);if(!t[n].support.csstransitions)return l.addClass(s.hidden).removeClass(s.opened),e.removeClass(s.hidden).addClass(s.opened),this.trigger("openPanel:start",e),void this.trigger("openPanel:finish",e);o.not(e).removeClass(s.subopened);for(var d=e.data(a.parent);d;)d=d.closest("."+s.panel),d.is("."+s.vertical)||d.addClass(s.subopened),d=d.data(a.parent);o.removeClass(s.highest).not(l).not(e).addClass(s.hidden),e.removeClass(s.hidden);var c=function(){l.removeClass(s.opened),e.addClass(s.opened),e.hasClass(s.subopened)?(l.addClass(s.highest),e.removeClass(s.subopened)):(l.addClass(s.subopened),e.addClass(s.highest)),this.trigger("openPanel:start",e)},h=function(){l.removeClass(s.highest).addClass(s.hidden),e.removeClass(s.highest),this.trigger("openPanel:finish",e)};i&&!e.hasClass(s.noanimation)?setTimeout(function(){r.__transitionend(e,function(){h.call(r)},r.conf.transitionDuration),c.call(r)},this.conf.openingInterval):(c.call(this),h.call(this))}this.trigger("openPanel:after",e)}},closePanel:function(t){this.trigger("closePanel:before",t);var e=t.parent();e.hasClass(s.vertical)&&(e.removeClass(s.opened),this.trigger("closePanel",t)),this.trigger("closePanel:after",t)},closeAllPanels:function(){this.trigger("closeAllPanels:before"),this.$pnls.find("."+s.listview).children().removeClass(s.selected).filter("."+s.vertical).removeClass(s.opened);var t=this.$pnls.children("."+s.panel),e=t.first();this.$pnls.children("."+s.panel).not(e).removeClass(s.subopened).removeClass(s.opened).removeClass(s.highest).addClass(s.hidden),this.openPanel(e),this.trigger("closeAllPanels:after")},togglePanel:function(t){var e=t.parent();e.hasClass(s.vertical)&&this[e.hasClass(s.opened)?"closePanel":"openPanel"](t)},setSelected:function(t){this.trigger("setSelected:before",t),this.$menu.find("."+s.listview).children("."+s.selected).removeClass(s.selected),t.addClass(s.selected),this.trigger("setSelected:after",t)},bind:function(t,e){this.cbck[t]=this.cbck[t]||[],this.cbck[t].push(e)},trigger:function(){var t=this,e=Array.prototype.slice.call(arguments),n=e.shift();if(this.cbck[n])for(var i=0,s=this.cbck[n].length;i<s;i++)this.cbck[n][i].apply(t,e)},matchMedia:function(t,e,n){var i={yes:e,no:n};this.mtch[t]=this.mtch[t]||[],this.mtch[t].push(i)},_initAddons:function(){this.trigger("initAddons:before");var e;for(e in t[n].addons)t[n].addons[e].add.call(this),t[n].addons[e].add=function(){};for(e in t[n].addons)t[n].addons[e].setup.call(this);this.trigger("initAddons:after")},_initExtensions:function(){this.trigger("initExtensions:before");var t=this;this.opts.extensions.constructor===Array&&(this.opts.extensions={all:this.opts.extensions});for(var e in this.opts.extensions)this.opts.extensions[e]=this.opts.extensions[e].length?"mm-"+this.opts.extensions[e].join(" mm-"):"",this.opts.extensions[e]&&!function(e){t.matchMedia(e,function(){this.$menu.addClass(this.opts.extensions[e])},function(){this.$menu.removeClass(this.opts.extensions[e])})}(e);this.trigger("initExtensions:after")},_initMenu:function(){this.trigger("initMenu:before");this.conf.clone&&(this.$orig=this.$menu,this.$menu=this.$orig.clone(),this.$menu.add(this.$menu.find("[id]")).filter("[id]").each(function(){t(this).attr("id",s.mm(t(this).attr("id")))})),this.opts.initMenu.call(this,this.$menu,this.$orig),this.$menu.attr("id",this.$menu.attr("id")||this.__getUniqueId()),this.$pnls=t('<div class="'+s.panels+'" />').append(this.$menu.children(this.conf.panelNodetype)).prependTo(this.$menu);var e=[s.menu];this.opts.slidingSubmenus||e.push(s.vertical),this.$menu.addClass(e.join(" ")).parent().addClass(s.wrapper),this.trigger("initMenu:after")},_initPanels:function(e){this.trigger("initPanels:before",e),e=e||this.$pnls.children(this.conf.panelNodetype);var n=t(),i=this,a=function(e){e.filter(this.conf.panelNodetype).each(function(){if($panel=i._initPanel(t(this)),$panel){i._initNavbar($panel),i._initListview($panel),n=n.add($panel);var e=$panel.children("."+s.listview).children("li").children(i.conf.panelNodeType).add($panel.children("."+i.conf.classNames.panel));e.length&&a.call(i,e)}})};a.call(this,e),this.opts.initPanels.call(this,n),this.trigger("initPanels:after",n)},_initPanel:function(t){this.trigger("initPanel:before",t);if(this.__refactorClass(t,this.conf.classNames.panel,"panel"),this.__refactorClass(t,this.conf.classNames.nopanel,"nopanel"),this.__refactorClass(t,this.conf.classNames.vertical,"vertical"),this.__refactorClass(t,this.conf.classNames.inset,"inset"),t.filter("."+s.inset).addClass(s.nopanel),t.hasClass(s.nopanel))return!1;if(t.hasClass(s.panel))return t;var e=t.hasClass(s.vertical)||!this.opts.slidingSubmenus;t.removeClass(s.vertical);var n=t.attr("id")||this.__getUniqueId();t.removeAttr("id"),t.is("ul, ol")&&(t.wrap("<div />"),t=t.parent()),t.addClass(s.panel+" "+s.hidden).attr("id",n);var i=t.parent("li");return e?t.add(i).addClass(s.vertical):t.appendTo(this.$pnls),i.length&&(i.data(a.child,t),t.data(a.parent,i)),this.trigger("initPanel:after",t),t},_initNavbar:function(e){if(this.trigger("initNavbar:before",e),!e.children("."+s.navbar).length){var i=e.data(a.parent),r=t('<div class="'+s.navbar+'" />'),o=t[n].i18n(this.opts.navbar.title),l=!1;if(i&&i.length){if(i.hasClass(s.vertical))return;if(i.parent().is("."+s.listview))var d=i.children("a, span").not("."+s.next);else var d=i.closest("."+s.panel).find('a[href="#'+e.attr("id")+'"]');d=d.first(),i=d.closest("."+s.panel);var c=i.attr("id");switch(o=d.text(),this.opts.navbar.titleLink){case"anchor":l=d.attr("href");break;case"parent":l="#"+c}r.append('<a class="'+s.btn+" "+s.prev+'" href="#'+c+'" />')}else if(!this.opts.navbar.title)return;this.opts.navbar.add&&e.addClass(s.hasnavbar),r.append('<a class="'+s.title+'"'+(l?' href="'+l+'"':"")+">"+o+"</a>").prependTo(e),this.trigger("initNavbar:after",e)}},_initListview:function(e){this.trigger("initListview:before",e);var n=this.__childAddBack(e,"ul, ol");this.__refactorClass(n,this.conf.classNames.nolistview,"nolistview"),n.filter("."+this.conf.classNames.inset).addClass(s.nolistview);var i=n.not("."+s.nolistview).addClass(s.listview).children();this.__refactorClass(i,this.conf.classNames.selected,"selected"),this.__refactorClass(i,this.conf.classNames.divider,"divider"),this.__refactorClass(i,this.conf.classNames.spacer,"spacer");var r=e.data(a.parent);if(r&&r.parent().is("."+s.listview)&&!r.children("."+s.next).length){var o=r.children("a, span").first(),l=t('<a class="'+s.next+'" href="#'+e.attr("id")+'" />').insertBefore(o);o.is("span")&&l.addClass(s.fullsubopen)}this.trigger("initListview:after",e)},_initOpened:function(){this.trigger("initOpened:before");var t=this.$pnls.find("."+s.listview).children("."+s.selected).removeClass(s.selected).last().addClass(s.selected),e=t.length?t.closest("."+s.panel):this.$pnls.children("."+s.panel).first();this.openPanel(e,!1),this.trigger("initOpened:after")},_initAnchors:function(){var e=this;o.$body.on(r.click+"-oncanvas","a[href]",function(i){var a=t(this),r=!1,o=e.$menu.find(a).length;for(var l in t[n].addons)if(t[n].addons[l].clickAnchor.call(e,a,o)){r=!0;break}var d=a.attr("href");if(!r&&o&&d.length>1&&"#"==d.slice(0,1))try{var c=t(d,e.$menu);c.is("."+s.panel)&&(r=!0,e[a.parent().hasClass(s.vertical)?"togglePanel":"openPanel"](c))}catch(h){}if(r&&i.preventDefault(),!r&&o&&a.is("."+s.listview+" > li > a")&&!a.is('[rel="external"]')&&!a.is('[target="_blank"]')){e.__valueOrFn(e.opts.onClick.setSelected,a)&&e.setSelected(t(i.target).parent());var f=e.__valueOrFn(e.opts.onClick.preventDefault,a,"#"==d.slice(0,1));f&&i.preventDefault(),e.__valueOrFn(e.opts.onClick.close,a,f)&&e.close()}})},_initMatchMedia:function(){var t=this;this._fireMatchMedia(),o.$wndw.on(r.resize,function(e){t._fireMatchMedia()})},_fireMatchMedia:function(){for(var t in this.mtch)for(var e=window.matchMedia&&window.matchMedia(t).matches?"yes":"no",n=0;n<this.mtch[t].length;n++)this.mtch[t][n][e].call(this)},_getOriginalMenuId:function(){var t=this.$menu.attr("id");return this.conf.clone&&t&&t.length&&(t=s.umm(t)),t},__api:function(){var e=this,n={};return t.each(this._api,function(t){var i=this;n[i]=function(){var t=e[i].apply(e,arguments);return"undefined"==typeof t?n:t}}),n},__valueOrFn:function(t,e,n){return"function"==typeof t?t.call(e[0]):"undefined"==typeof t&&"undefined"!=typeof n?n:t},__refactorClass:function(t,e,n){return t.filter("."+e).removeClass(e).addClass(s[n])},__findAddBack:function(t,e){return t.find(e).add(t.filter(e))},__childAddBack:function(t,e){return t.children(e).add(t.filter(e))},__filterListItems:function(t){return t.not("."+s.divider).not("."+s.hidden)},__filterListItemAnchors:function(t){return this.__filterListItems(t).children("a").not("."+s.next)},__transitionend:function(t,e,n){var i=!1,s=function(n){"undefined"!=typeof n&&n.target!=t[0]||(i||(t.unbind(r.transitionend),t.unbind(r.webkitTransitionEnd),e.call(t[0])),i=!0)};t.on(r.transitionend,s),t.on(r.webkitTransitionEnd,s),setTimeout(s,1.1*n)},__getUniqueId:function(){return s.mm(t[n].uniqueId++)}},t.fn[n]=function(i,s){e(),i=t.extend(!0,{},t[n].defaults,i),s=t.extend(!0,{},t[n].configuration,s);var a=t();return this.each(function(){var e=t(this);if(!e.data(n)){var r=new t[n](e,i,s);r.$menu.data(n,r.__api()),a=a.add(r.$menu)}}),a},t[n].i18n=function(){var e={};return function(n){switch(typeof n){case"object":return t.extend(e,n),e;case"string":return e[n]||n;case"undefined":default:return e}}}(),t[n].support={touch:"ontouchstart"in window||navigator.msMaxTouchPoints||!1,csstransitions:function(){return"undefined"==typeof Modernizr||"undefined"==typeof Modernizr.csstransitions||Modernizr.csstransitions}(),csstransforms:function(){return"undefined"==typeof Modernizr||"undefined"==typeof Modernizr.csstransforms||Modernizr.csstransforms}(),csstransforms3d:function(){return"undefined"==typeof Modernizr||"undefined"==typeof Modernizr.csstransforms3d||Modernizr.csstransforms3d}()};var s,a,r,o}}(jQuery),/*
     * jQuery mmenu offCanvas add-on
     * mmenu.frebsite.nl
     *
     * Copyright (c) Fred Heusschen
     */
        function(t){var e="mmenu",n="offCanvas";t[e].addons[n]={setup:function(){if(this.opts[n]){var s=this,a=this.opts[n],o=this.conf[n];r=t[e].glbl,this._api=t.merge(this._api,["open","close","setPage"]),"object"!=typeof a&&(a={}),"top"!=a.position&&"bottom"!=a.position||(a.zposition="front"),a=this.opts[n]=t.extend(!0,{},t[e].defaults[n],a),"string"!=typeof o.pageSelector&&(o.pageSelector="> "+o.pageNodetype),r.$allMenus=(r.$allMenus||t()).add(this.$menu),this.vars.opened=!1;var l=[i.offcanvas];"left"!=a.position&&l.push(i.mm(a.position)),"back"!=a.zposition&&l.push(i.mm(a.zposition)),t[e].support.csstransforms||l.push(i["no-csstransforms"]),t[e].support.csstransforms3d||l.push(i["no-csstransforms3d"]),this.bind("initMenu:after",function(){this.setPage(r.$page),this._initBlocker(),this["_initWindow_"+n](),this.$menu.addClass(l.join(" ")).parent("."+i.wrapper).removeClass(i.wrapper),this.$menu[o.menuInsertMethod](o.menuInsertSelector);var t=window.location.hash;if(t){var e=this._getOriginalMenuId();e&&e==t.slice(1)&&this.open()}}),this.bind("initExtensions:after",function(){for(var t=[i.mm("widescreen"),i.mm("iconbar")],e=0;e<t.length;e++)for(var n in this.opts.extensions)if(this.opts.extensions[n].indexOf(t[e])>-1){!function(e,n){s.matchMedia(e,function(){r.$html.addClass(t[n])},function(){r.$html.removeClass(t[n])})}(n,e);break}}),this.bind("open:start:sr-aria",function(){this.__sr_aria(this.$menu,"hidden",!1)}),this.bind("close:finish:sr-aria",function(){this.__sr_aria(this.$menu,"hidden",!0)}),this.bind("initMenu:after:sr-aria",function(){this.__sr_aria(this.$menu,"hidden",!0)})}},add:function(){i=t[e]._c,s=t[e]._d,a=t[e]._e,i.add("offcanvas slideout blocking modal background opening blocker page no-csstransforms3d"),s.add("style")},clickAnchor:function(t,e){var s=this;if(this.opts[n]){var a=this._getOriginalMenuId();if(a&&t.is('[href="#'+a+'"]')){if(e)return!0;var o=t.closest("."+i.menu);if(o.length){var l=o.data("mmenu");if(l&&l.close)return l.close(),s.__transitionend(o,function(){s.open()},s.conf.transitionDuration),!0}return this.open(),!0}if(r.$page)return a=r.$page.first().attr("id"),a&&t.is('[href="#'+a+'"]')?(this.close(),!0):void 0}}},t[e].defaults[n]={position:"left",zposition:"back",blockUI:!0,moveBackground:!0},t[e].configuration[n]={pageNodetype:"div",pageSelector:null,noPageSelector:[],wrapPageIfNeeded:!0,menuInsertMethod:"prependTo",menuInsertSelector:"body"},t[e].prototype.open=function(){if(this.trigger("open:before"),!this.vars.opened){var t=this;this._openSetup(),setTimeout(function(){t._openFinish()},this.conf.openingInterval),this.trigger("open:after")}},t[e].prototype._openSetup=function(){var e=this,o=this.opts[n];this.closeAllOthers(),r.$page.each(function(){t(this).data(s.style,t(this).attr("style")||"")}),r.$wndw.trigger(a.resize+"-"+n,[!0]);var l=[i.opened];o.blockUI&&l.push(i.blocking),"modal"==o.blockUI&&l.push(i.modal),o.moveBackground&&l.push(i.background),"left"!=o.position&&l.push(i.mm(this.opts[n].position)),"back"!=o.zposition&&l.push(i.mm(this.opts[n].zposition)),r.$html.addClass(l.join(" ")),setTimeout(function(){e.vars.opened=!0},this.conf.openingInterval),this.$menu.addClass(i.opened)},t[e].prototype._openFinish=function(){var t=this;this.__transitionend(r.$page.first(),function(){t.trigger("open:finish")},this.conf.transitionDuration),this.trigger("open:start"),r.$html.addClass(i.opening)},t[e].prototype.close=function(){if(this.trigger("close:before"),this.vars.opened){var e=this;this.__transitionend(r.$page.first(),function(){e.$menu.removeClass(i.opened);var a=[i.opened,i.blocking,i.modal,i.background,i.mm(e.opts[n].position),i.mm(e.opts[n].zposition)];r.$html.removeClass(a.join(" ")),r.$page.each(function(){t(this).attr("style",t(this).data(s.style))}),e.vars.opened=!1,e.trigger("close:finish")},this.conf.transitionDuration),this.trigger("close:start"),r.$html.removeClass(i.opening),this.trigger("close:after")}},t[e].prototype.closeAllOthers=function(){r.$allMenus.not(this.$menu).each(function(){var n=t(this).data(e);n&&n.close&&n.close()})},t[e].prototype.setPage=function(e){this.trigger("setPage:before",e);var s=this,a=this.conf[n];e&&e.length||(e=r.$body.find(a.pageSelector),a.noPageSelector.length&&(e=e.not(a.noPageSelector.join(", "))),e.length>1&&a.wrapPageIfNeeded&&(e=e.wrapAll("<"+this.conf[n].pageNodetype+" />").parent())),e.each(function(){t(this).attr("id",t(this).attr("id")||s.__getUniqueId())}),e.addClass(i.page+" "+i.slideout),r.$page=e,this.trigger("setPage:after",e)},t[e].prototype["_initWindow_"+n]=function(){r.$wndw.off(a.keydown+"-"+n).on(a.keydown+"-"+n,function(t){if(r.$html.hasClass(i.opened)&&9==t.keyCode)return t.preventDefault(),!1});var t=0;r.$wndw.off(a.resize+"-"+n).on(a.resize+"-"+n,function(e,n){if(1==r.$page.length&&(n||r.$html.hasClass(i.opened))){var s=r.$wndw.height();(n||s!=t)&&(t=s,r.$page.css("minHeight",s))}})},t[e].prototype._initBlocker=function(){var e=this;this.opts[n].blockUI&&(r.$blck||(r.$blck=t('<div id="'+i.blocker+'" class="'+i.slideout+'" />')),r.$blck.appendTo(r.$body).off(a.touchstart+"-"+n+" "+a.touchmove+"-"+n).on(a.touchstart+"-"+n+" "+a.touchmove+"-"+n,function(t){t.preventDefault(),t.stopPropagation(),r.$blck.trigger(a.mousedown+"-"+n)}).off(a.mousedown+"-"+n).on(a.mousedown+"-"+n,function(t){t.preventDefault(),r.$html.hasClass(i.modal)||(e.closeAllOthers(),e.close())}))};var i,s,a,r}(jQuery),/*
     * jQuery mmenu scrollBugFix add-on
     * mmenu.frebsite.nl
     *
     * Copyright (c) Fred Heusschen
     */
        function(t){var e="mmenu",n="scrollBugFix";t[e].addons[n]={setup:function(){var s=this.opts[n];this.conf[n];r=t[e].glbl,t[e].support.touch&&this.opts.offCanvas&&this.opts.offCanvas.blockUI&&("boolean"==typeof s&&(s={fix:s}),"object"!=typeof s&&(s={}),s=this.opts[n]=t.extend(!0,{},t[e].defaults[n],s),s.fix&&(this.bind("open:start",function(){this.$pnls.children("."+i.opened).scrollTop(0)}),this.bind("initMenu:after",function(){this["_initWindow_"+n]()})))},add:function(){i=t[e]._c,s=t[e]._d,a=t[e]._e},clickAnchor:function(t,e){}},t[e].defaults[n]={fix:!0},t[e].prototype["_initWindow_"+n]=function(){r.$docu.off(a.touchmove+"-"+n).on(a.touchmove+"-"+n,function(t){r.$html.hasClass(i.opened)&&t.preventDefault()});var e=!1;r.$body.off(a.touchstart+"-"+n).on(a.touchstart+"-"+n,"."+i.panels+"> ."+i.opened,function(t){r.$html.hasClass(i.opened)&&(e||(e=!0,0===t.currentTarget.scrollTop?t.currentTarget.scrollTop=1:t.currentTarget.scrollHeight===t.currentTarget.scrollTop+t.currentTarget.offsetHeight&&(t.currentTarget.scrollTop-=1),e=!1))}).off(a.touchmove+"-"+n).on(a.touchmove+"-"+n,"."+i.panels+"> ."+i.opened,function(e){r.$html.hasClass(i.opened)&&t(this)[0].scrollHeight>t(this).innerHeight()&&e.stopPropagation()}),r.$wndw.off(a.orientationchange+"-"+n).on(a.orientationchange+"-"+n,function(){that.$pnls.children("."+i.opened).scrollTop(0).css({"-webkit-overflow-scrolling":"auto"}).css({"-webkit-overflow-scrolling":"touch"})})};var i,s,a,r}(jQuery),/*
     * jQuery mmenu screenReader add-on
     * mmenu.frebsite.nl
     *
     * Copyright (c) Fred Heusschen
     */
        function(t){var e="mmenu",n="screenReader";t[e].addons[n]={setup:function(){var s=this,a=this.opts[n],o=this.conf[n];r=t[e].glbl,"boolean"==typeof a&&(a={aria:a,text:a}),"object"!=typeof a&&(a={}),a=this.opts[n]=t.extend(!0,{},t[e].defaults[n],a),a.aria&&(this.bind("initAddons:after",function(){this.bind("initMenu:after",function(){this.trigger("initMenu:after:sr-aria")}),this.bind("initNavbar:after",function(){this.trigger("initNavbar:after:sr-aria",arguments[0])}),this.bind("openPanel:start",function(){this.trigger("openPanel:start:sr-aria",arguments[0])}),this.bind("close:start",function(){this.trigger("close:start:sr-aria")}),this.bind("close:finish",function(){this.trigger("close:finish:sr-aria")}),this.bind("open:start",function(){this.trigger("open:start:sr-aria")}),this.bind("open:finish",function(){this.trigger("open:finish:sr-aria")})}),this.bind("updateListview",function(){this.$pnls.find("."+i.listview).children().each(function(){s.__sr_aria(t(this),"hidden",t(this).is("."+i.hidden))})}),this.bind("openPanel:start",function(t){var e=this.$menu.find("."+i.panel).not(t).not(t.parents("."+i.panel)),n=t.add(t.find("."+i.vertical+"."+i.opened).children("."+i.panel));this.__sr_aria(e,"hidden",!0),this.__sr_aria(n,"hidden",!1)}),this.bind("closePanel",function(t){this.__sr_aria(t,"hidden",!0)}),this.bind("initPanels:after",function(e){var n=e.find("."+i.prev+", ."+i.next).each(function(){s.__sr_aria(t(this),"owns",t(this).attr("href").replace("#",""))});this.__sr_aria(n,"haspopup",!0)}),this.bind("initNavbar:after",function(t){var e=t.children("."+i.navbar);this.__sr_aria(e,"hidden",!t.hasClass(i.hasnavbar))}),a.text&&(this.bind("initlistview:after",function(t){var e=t.find("."+i.listview).find("."+i.fullsubopen).parent().children("span");this.__sr_aria(e,"hidden",!0)}),"parent"==this.opts.navbar.titleLink&&this.bind("initNavbar:after",function(t){var e=t.children("."+i.navbar),n=!!e.children("."+i.prev).length;this.__sr_aria(e.children("."+i.title),"hidden",n)}))),a.text&&(this.bind("initAddons:after",function(){this.bind("setPage:after",function(){this.trigger("setPage:after:sr-text",arguments[0])})}),this.bind("initNavbar:after",function(n){var s=n.children("."+i.navbar),a=s.children("."+i.title).text(),r=t[e].i18n(o.text.closeSubmenu);a&&(r+=" ("+a+")"),s.children("."+i.prev).html(this.__sr_text(r))}),this.bind("initlistview:after",function(n){n.find("."+i.listview).children("li").children("."+i.next).each(function(){var n=t(this),a=$prev.nextAll("span, a").first().text(),r=t[e].i18n(o.text[$prev.parent().is("."+i.vertical)?"toggleSubmenu":"openSubmenu"]);a&&(r+=" ("+a+")"),n.html(s.__sr_text(r))})}))},add:function(){i=t[e]._c,s=t[e]._d,a=t[e]._e,i.add("sronly")},clickAnchor:function(t,e){}},t[e].defaults[n]={aria:!0,text:!0},t[e].configuration[n]={text:{closeMenu:"Close menu",closeSubmenu:"Close submenu",openSubmenu:"Open submenu",toggleSubmenu:"Toggle submenu"}},t[e].prototype.__sr_aria=function(t,e,n){t.prop("aria-"+e,n)[n?"attr":"removeAttr"]("aria-"+e,n)},t[e].prototype.__sr_text=function(t){return'<span class="'+i.sronly+'">'+t+"</span>"};var i,s,a,r}(jQuery);
    return true;
}));
