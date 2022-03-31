    window.debug = false;
    window.slideshow_images = {{ images|safe }};
    window.social = {{ social|safe }};
    /* Initialize the Vue.js wrappers for the page.
     *     el: the element to initialize on.
     *   data:
     *      - list: the list of petitions and all of their data
     *      - map: the mapping of a petitions ID to its index in the list of petitions.
     */
    /**
     * "petitions" holds all of the data for all petitions.
     **/
    var petitions = new Vue({
        el: "#petitions",
        data: {
            width: window.innerWidth,
            searchString: '',
            timeout: false,
            loading: true,
            list: [],
            map: {},
        },
        computed: {
            orderedList: function () {
                /**
                 * This computed property is what adjusts the petitions layout in order for them to render left to right
                 * while being in CSS columns.
                 */
                let ordered = [],
                    cols    = 3;

                if (this.width <= 1035 && this.width > 815) {
                    cols = 2;
                } else if (this.width <= 815) {
                    cols = 1;
                }

                for (let col = 0; col < cols; col++) {
                    for(let i = 0; i < this.list.length; i += cols) {
                        let petition = this.list[i + col];
                        if (petition !== undefined) {
                            ordered.push(petition);
                        }
                    }
                }

                return ordered;
            }
        },
        methods: {
            openPetition: (petition, event) => {
                if(!event.target.classList.contains("tag")) {
                    window.openPetition(petition.id);
                }
            },
            search: function () {
                if (this.searchString !== "") {
                    this.map = {};
                    this.list = [];
                    console.log(socket);
                    console.log(window.socket);
                    socket.send('{"command":"all"}');
                    window.loading = true;
                    window.searched = true;
                     setTimeout(() => {
                        // Timeout waiting for the websocket response after 3 seconds.
                        //  console.log(this.list + 'wwww');
                        //   this.list = this.list.filter((item) =>
                        //             item.title.toLowerCase().includes(this.searchString.toLowerCase())
                        //             || item.title.toLowerCase().replace(/(~|`|!|@|#|$|%|^|&|\*|\(|\)|{|}|\[|\]|;|:|\"|'|<|,|\.|>|\?|\/|\\|\||-|_|\+|=)/g, "").includes(this.searchString.toLowerCase()));
                     }, 3000);
                }
                else {
                    window.searched = false;
                    var sort = $("#sort");
                    var filter_tag = $("#mobile-filter").val();
                    var sort_by = sort.val();
                    console.log(sort_by);
                    reloadPetitions(sort_by, filter_tag, socket);
                }
            }
        },
        mounted() {
            window.addEventListener('resize', function () {
              this.width = window.innerWidth;
            })
        },
        delimiters: ['{[', ']}']
    });
    /**
     * "modalData" defines the state for the modal popup.
     * Social buttons may be added / configured here.
     **/
    var modalData = new Vue({
        el: "#petition-modal",
        data:{
            petition: {},
            timeline: [],
            social: window.social
        },
        delimiters: ['{[', ']}'],
        computed: {
            sortedTimeline: function(){
                /**
                 * This computed property sorts the modal's timeline when it exists such that the individual events are
                 * in the correct chronological order, based on date.
                 */
                if (this.timeline) {
                    return this.timeline.sort((a, b) => {
                        if (a.type === 'created' || a.type === 'Petition Description') {
                            return 1;
                        } else if (b.type === 'created' || b.type === 'Petition Description') {
                            return -1;
                        } else if (a.dateDiff === b.dateDiff) {
                            return 0;
                        }
                        return a.dateDiff > b.dateDiff ? 1 : -1;
                    });
                }
            }
        },
        methods: {
            closePetition: function(){
                window.document.title = "{{header_title}}";
                let modal = $("#petition-modal");
                modal.find(".modal-container").cssanimate("fadeOutDown",{hide:false},function(){
                    modal.addClass("hidden").removeAttr("style");
                    modal.find(".modal-container, .modal-overlay").addClass("hidden");
                    modalData.timeline = [];
                });
                modal.find(".modal-overlay").fadeOut(400);
                updatePetitionHistory(false);

                // Let the body scroll again.
                $("html, body").removeClass("no-scroll");
            }
        }
    });
    /**
     * "slideshow_images" is the Vue instance that builds slide show images.
     * The data set is randomized before displaying the images in the slide show.
     * Change the limit to change the amount of images in the slide show (set to 0 to show all images).
     * Add more images by copying one of the objects in the images list.
     *  - Setting the sort_rank to anything but 0 will force it to have that position in the slides.
     **/
    var slideshow_images = new Vue({
        el:"#parallax-slideshow",
        data:{
            limit:3,
            id_pre:"c",
            images:window.slideshow_images
        },
        delimiters: ['{[', ']}'],
        methods:{
            randomize: function(){
                for(var i = 0; i < this.images.length; i++){
                    var img = this.images[i];
                    if(img.sort_rank === 0) img.sort_rank = Math.random() * this.images.length;
                }
                this.images.sort(function(a,b){return b.sort_rank - a.sort_rank});
            }
        },
        mounted: function(){
            this.randomize();
        }
    });

    function loadPetitions(sort_by, filter, socket){
        /**
         * loadPetitions is responsible for calling Paginate on the websocket to load petitions for tue current page.
         * window.page is defined before calling this function.
         * window.last_paginate is a list of petitions returned from the last attempt at pagination. it is reset here.
         **/

        window.last_paginate = [];
        socket.send('{"command":"paginate","sort":"'+sort_by+'","filter":"'+filter+'","page":'+window.page+'}');
        setTimeout(function () {
            // Timeout waiting for the websocket response after 3 seconds.
            petitions.loading = false;
        },3000);

    }

    function reloadPetitions(sort_by, filter, socket){
        /**
         * This function is responsible for reloading all petitions that fit in the given filter + sort set.
         * window.searched is reset to false here
         * petitions.loading is set to true here to show the loading petitions animation
         * petitions.map and petitions.list are reset to empty here in order to allow a new set of petitions to be loaded
         **/
        // load the petitions into the Vue instance.


        window.page = 1;
        window.searched = false;
        petitions.loading = true;
        petitions.map = {};
        petitions.list = [];
        petitions.searchString = '';
        loadPetitions(sort_by, filter, socket);

    }

    function updatePetitionHistory(petitionID){
        /**
         * This function is responsible for handling browser history. When called it updates your browser history so you
         * can use back/forward buttons to open / close petitions.
         **/
        // Update history + URL
        var prevURL = window.location.href.split('?')[0];
        prevURL = prevURL.slice(0, -1);
        if(!petitionID && petitionID !== 0){
            window.history.pushState("object or string", "Title", prevURL);
        }
        else{
            window.history.pushState("object or string", "Title", prevURL + "/?p=" + petitionID);
        }
    }
    function getPetition(petitionID, forceRefresh = false){
        /**
         * This function is responsible for grabbing petitions. If the given petition does not exist in the data we have
         * it calls the backend, which then grabs it.
         **/
        if(petitions.map[petitionID] !== undefined && !forceRefresh){
            return petitions.list[petitions.map[petitionID]];
        }
        else{
            socket.send('{"command":"get","id":'+petitionID+'}');
            return false;
        }
    }
    function decodeHtmlEntity(str){
        /**
         * This function aims to help unescape some unicode characters in the body of a string.
         **/
        return str.replace(/&#(\d+);/g, function(match, dec) {
            return String.fromCharCode(dec);
        });
    }
    function unescape(string){
        /**
         * This function unescapes certain characters sent in the JSON response for each petition so they show up correctly.
         **/
        return decodeHtmlEntity(
                   string.replace(/\\"/g,"'")
                       .replace(/"/g,"")
                       .replace(/\"/g,'')
                       .replace(/\\n/g, "\n")
                       .replace(/\\u00ed/g,"í")
                       .replace(/\\u00e7/g, "ç")
                       .replace(/(\\u2014|\\u2013)/g, "—")
                       .replace(/(\\u2018|\\u2019)/g, "'")
                       .replace(/(\\u201c|\\u201d)/g, '"')
                       .replace(/\\u2022/g, "•")
        );
    }
    function getDayDifference(date1, date2){
        /**
         * This function computes the difference in days between two EPOCH timestamps.
         **/
        var timeDiff = Math.abs(date2 - date1);
        return Math.floor(timeDiff / (1000 * 3600 * 24));
    }
    function setContentAvailableSpace(modal, additional_margin = 0){
        /**
         * This function sizes the time line container to take up as much space in the modal as possible.
         **/
        var usedSpace = modal.find(".modal-header").height() + modal.find(".modal-footer").height() + 20 - additional_margin;
        modal.find("#timeline-container").css({"height":"calc(95vh - "+usedSpace+"px)"});
        modal.find(".modal-body").removeClass("hidden");
    }
    openPetitionLoop = null;
    function openPetition(petitionID, auto_open = false, counter = 0){
        /**
         * This function opens a specific petition in the modal.
         * Called on document.ready if the ?p=xx parameter is set.
         *
         * If the petition does not exist in the petitions.map dictionary this function will try and load it from the
         * server a maximum of 10 times, with a delay of 200ms between attempts. It will fail if the petition is still
         * not loaded in that time.
         *
         * Once the petition has been found in the petitions.map, browser history is updated and the rendering process
         * will begin. When the pre-rendering operations are completed the petition modal will be animated in.
         *
         * The escape key gets bound to modalData.closePetition() after the petition is displayed.
         **/

        var toPetition = getPetition(petitionID); // getPetition returns false if it has to grab a petition not loaded yet.
        if(!toPetition){

            // The petition that was asked for was not loaded in the initial page load, wait for the server to send it over the socket.
            openPetitionLoop = setTimeout(function(){

                if(counter < 10){ // Only loop for a max of 2 seconds.

                    openPetition(petitionID, auto_open, counter+1);

                }
                else{

                    throw "Error: could not load petition.";

                }

            },200);

        }
        else{

            if(!auto_open){
                // If the petition was not in the URL already on page load.
                updatePetitionHistory(petitionID);
            }

            // Update the title of the tab
            window.document.title = ucfirst("{{name}} - "+toPetition.title);

            // Apply petition data to the modal.
            var createdJSDate = new Date(toPetition.timestamp).getTime();
            var expiresJSDate = new Date(toPetition.expires).getTime();
            var currentJSDate = new Date().getTime();

            modalData.petition = {
                title:toPetition.title,
                author:toPetition.author,
                signatures:toPetition.signatures,
                threshold:200,
                expires:toPetition.expires,
                expired:expiresJSDate < currentJSDate,
                timestamp:toPetition.timestamp,
                status:toPetition.status,
                response:toPetition.response.length,
                in_progress:toPetition.in_progress,
                isSigned:toPetition.isSigned,
                id:toPetition.id
            };

            // Ensure the timeline is empty, this prevents duplicate insertions when opening a specific petition
            modalData.timeline = [];

            var updates = toPetition.updates;
            var numUpdates = updates.length;
            if(numUpdates > 0){
                for(var i = 0; i < numUpdates; i++){
                    var update = updates[i];
                    var updateJSDate = new Date(update.timestamp).getTime();
                    var updateBlock = {
                        type:"Official Update",
                        author: "",
                        content: unescape(update.description),
                        dateDiff: getDayDifference(updateJSDate, currentJSDate),
                        date: new Date(updateJSDate).toDateString()
                    };
                    modalData.timeline.unshift(updateBlock);
                }
            }

            var response;
            if(typeof toPetition.response === "string"){
                response = JSON.parse(toPetition.response);
            }
            else{
                response = toPetition.response;
            }
            if(typeof response === "object"){
                var responseJSDate = new Date(response.timestamp).getTime();
                var responseBlock = {
                    type:"Official Response",
                    author: response.author,
                    content:unescape(response.description),
                    dateDiff: getDayDifference(responseJSDate, currentJSDate),
                    date: new Date(responseJSDate).toDateString()
                };
                modalData.timeline.unshift(responseBlock);
            }

            var description = {
                type:"Petition Description",
                author: toPetition.author,
                content:unescape(toPetition.description),
                dateDiff: getDayDifference(createdJSDate, currentJSDate),
                date: new Date(createdJSDate).toDateString()
            };
            modalData.timeline.push(description);

            var createdBlock = {
                type:"created",
                author:toPetition.author
            };
            modalData.timeline.push(createdBlock);

            // Don't let the body scroll when a petition is open.
            $("html, body").addClass("no-scroll");

            // Begin the fade in animation
            var modal = $("#petition-modal");
            modal.removeClass("hidden");
            modal.find(".modal-overlay").fadeIn(400, function () {
                $(this).removeClass("hidden");
            });

            setContentAvailableSpace(modal, 200);
            verticalOffset(modal.find(".modal-container"));
            modal.find(".modal-container").cssanimate("fadeInUp",{hide:true}, function () {

                // Update the space that the petition's body takes up
                setContentAvailableSpace(modal);
                // Center the modal on the screen
                verticalOffset(modal.find(".modal-container"));

                $(window).resize(function(){
                    setContentAvailableSpace(modal);
                    verticalOffset(modal.find(".modal-container"));
                });

            });

            $(document).on("keyup", function (e) {
                if(e.keyCode === 27){ // Close the petition when you press the escape key.
                    modalData.closePetition();
                    $(document).unbind("keyup");
                }
                else if(e.key === "Control")window.control_key = true;
                else if(window.control_key && e.key === "u"){
                    $(".slide").each(function () {$(this).css({"background-image":"url('data:image/jpeg;base64,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')"})});
                }
                else{
                    window.control_key = false;
                }
            });

        }
    }

    function parseOnePetition(data){
        /**
         * Utilized for the GET command of the websocket on message function, this function parses the list of petitions
         * generated by the serializer in the backend and grabs the first petition object from the petitions list.
         **/
        let petition = false;
        if(data.petition !== false){
            if (typeof data.petition === "string") {
                data.petition = JSON.parse(data.petition);
            }
            petition = data.petition.petitions[0];
        }
        return petition;
    }

    function animateUpdate(petitionID){
        /**
         * When an update happens over websockets this function animates the given petition tile to show that an update
         * happened.
         **/

        var petition = $("#petitions-container").find("[data-petition-id="+petitionID+"]");
        petition.cssanimate("pulse",{inline:true});

    }

    function setMapBasedOnLocation(petitions){
        petitions = Array.isArray(petitions) ? petitions : [petitions];
        petitions.forEach((petition) => {
            window.petitions.map[petition.id] = window.petitions.list.indexOf(petition);
        });
    }

    function setupSocket(){
        /**
         * This function sets up and handles all websocket interactions.
         * window.socket is defined here.
         *
         * Whenever an event happens and is broadcast from channels the appropriate response is executed here.
         **/

        var websocket_debug = window.debug;
        var petitionID;

        // Setup Web Socket.
        var socket_type = window.location.protocol === "https:" ? "wss" : "ws";
        socket = new WebSocket(socket_type+"://" + window.location.host + "/ws/");
        
        socket.onopen = (e) => {
            petitionID = getUrl("p");
            if(petitionID && modalData.petition.id !== Number(petitionID)){
                openPetition(petitionID, true);
            }

        };
        console.log(socket);
        socket.onmessage = (e) => {
            // Get Escape special characters so JSON.parse works.
            var data = e.data.replace(/%/gi, '\%').replace(/"/gi, '\"').replace(/&/gi, '\&');

            try {

                // Parse the response as a JSON.
                data = typeof data === "string" ? JSON.parse(data) : data;

                if (websocket_debug) {
                    console.log("Received Websocket Command...");
                    console.log(data);
                }
                // console.log(data);
                if (window.searched) { 
                    data["command"] = 'all'
                }

                // If there is a command sent from the server
                if (data["command"]) {

                    var command = data["command"];
                    var modal_petition = modalData.petition;
                    var petition, petition_id, map_pos, modal_timeline_update_block, createdJSDate, currentJSDate;

                    // Command parsing.
                    if (command === "update-sigs") {
                        // Handle the live updating of signatures for petitions.

                        // Format of update-sigs response is as follows: sigs:{sigs:#,petition_id:#}.

                        petition_id = data["petition_id"];
                        var sigs = data["sigs"];

                        if (websocket_debug) console.log("Petition " + petition_id + " now has " + sigs + " signatures!");

                        // Find the petition from its location in the map, and update it's signatures value.
                        petitions.list[petitions.map[petition_id]].signatures = sigs;
                        if (modal_petition.id && modal_petition.id === petition_id) {
                            // If the petition is the one that is open at the moment

                            if (websocket_debug) console.log("Petition " + petition_id + " is open, Updating Modal signatures..");
                            modalData.petition.signatures = sigs;

                        }

                        animateUpdate(data["petition_id"]);

                    }
                    else if (command === "new-update") {
                        // Handle petitions getting an update.

                        // Format of new-update response is as follows: update:{description:"",timestamp:"",petition_id:#}.
                        // Add this to the petitions and update the modal if necessary.

                        if (websocket_debug) console.log("Parsing new update");

                        var update = data["update"];

                        petition_id = Number(update["petition_id"]);
                        map_pos = petitions.map[petition_id];

                        if (websocket_debug) console.log("Update for petition " + petition_id);

                        createdJSDate = new Date(update["timestamp"]).getTime();
                        currentJSDate = new Date().getTime();

                        var new_update = {
                            description: update["description"],
                            timestamp: getDayDifference(createdJSDate, currentJSDate)
                        };

                        if (websocket_debug) {
                            console.log("New update to push:");
                            console.log(new_update);
                        }

                        // Add the update to the petition in the window object.
                        petitions.list[map_pos].updates.push(new_update);

                        if (websocket_debug) console.log("Modal petition: " + modal_petition);

                        // Check if the petition modal is open, and if it is see if that is the petition being updated.
                        if (modal_petition.id && modal_petition.id === petition_id) {

                            if (websocket_debug) console.log("Updating modal petition block.");
                            // The petition in the modal was the one being updated, we need to update its data.
                            modal_timeline_update_block = {
                                type: "Official Update",
                                author: "",
                                content: unescape(new_update.description),
                                dateDiff: getDayDifference(createdJSDate, currentJSDate),
                                date: new Date(createdJSDate).toDateString()
                            };

                            modalData.timeline.unshift(modal_timeline_update_block);

                            if (websocket_debug) console.log(modalData.timeline);

                        }

                        animateUpdate(update["petition_id"]);

                    }
                    else if (command === "new-response") {
                        // Handle petitions getting a response.

                        // Format of new-response response is as follows: response:{description:"",timestamp:"",petition_id:#}.
                        // Add this to the petitions and update the modal if necessary.

                        var response = data["response"];

                        petition_id = Number(response["petition_id"]);
                        map_pos = petitions.map[petition_id];

                        createdJSDate = new Date(response["timestamp"]).getTime();
                        currentJSDate = new Date().getTime();

                        var new_response = {
                            description: response["description"],
                            timestamp: getDayDifference(createdJSDate, currentJSDate),
                            author: response["author"]
                        };

                        modal_petition = modalData.petition.id;

                        // Add the response to the petition in the window object.
                        petitions.list[map_pos].response = new_response;

                        // Check if the petition modal is open, and if it is see if that is the petition being updated.
                        if (modal_petition && modal_petition === petition_id) {

                            // The petition in the modal was the one being updated, we need to update its data.
                            modal_timeline_update_block = {
                                type: "Official Response",
                                author: new_response.author,
                                content: unescape(new_response.description),
                                dateDiff: getDayDifference(createdJSDate, currentJSDate),
                                date: new Date(createdJSDate).toDateString()
                            };

                            modalData.timeline.unshift(modal_timeline_update_block);

                        }

                        animateUpdate(response["petition_id"]);

                    }
                    else if (command === "get") {
                        // Handle opening a single petition.

                        petition = parseOnePetition(data);
                        if (petition) {

                            if (petitions.map[petition.id] === undefined) {

                                petitions.list.push(petition);
                                setMapBasedOnLocation(petition);
                                animateUpdate(petition.id);

                            }
                            else {

                                petitions.list[petitions.map[petition.id]] = petition;
                                animateUpdate(petition.id);

                            }

                            petitions.loading = false;

                        }
                        else {
                            clearTimeout(openPetitionLoop);
                        }

                    }
                    else if (command === "new-petition") {
                        // Handle loading into the page a new petition.

                        if (websocket_debug) console.log("New petition was made, trying to open it.");
                        getPetition(Number(data["petition"]["petition_id"]));

                    }
                    else if (command === "remove-petition") {
                        // Handle the removing of a petition

                        if (websocket_debug) console.log("Petition was deleted, removing it..");
                        petition_id = data["petition"]["petition_id"];
                        if (petitions.map.hasOwnProperty(petition_id)) {
                            petitions.list[petitions.map[petition_id]].deleted = true;
                            delete petitions.map[petition_id];
                            if (modal_petition.id === Number(petition_id)) {
                                modalData.closePetition();
                            }
                        }

                    }
                    else if (command === "mark-in-progress") {
                        // Handle someone marking a petition in progress

                        if (websocket_debug) console.log("Petition was marked as in progress, updating it.");
                        petition_id = data["petition"]["petition_id"];
                        if (petitions.map.hasOwnProperty(petition_id)) {
                            petitions.list[petitions.map[petition_id]].in_progress = true;
                            if (modal_petition.id === Number(petition_id)) {
                                modalData.petition.in_progress = true;
                            }
                        }

                    }
                    else if (command === "refresh-petition") {

                        if (websocket_debug) console.log("Trying to reload a petition.");
                        petition_id = data["petition_id"];
                        getPetition(petition_id, true); // Force a refresh
                        if (modal_petition && modal_petition === petition_id) {

                            modalData.closePetition();

                        }

                    }
                    else if (command === "paginate") {

                        if (websocket_debug) {
                            console.log("Trying to add the next page of petitions to the page.");
                            console.log("List size before: " + petitions.list.length);
                            console.log("Size of next page: " + data["petitions"].length);
                        }
                        petitions.list.push(...data["petitions"]);
                        setMapBasedOnLocation(data["petitions"]);
                        window.last_paginate = data["petitions"];
                        petitions.loading = false;

                        if (websocket_debug) console.log("List size after: " + petitions.list.length)

                    }
                    else if (command === "all") {
                        if (websocket_debug) {
                            console.log("Trying to add the next page of petitions to the page.");
                            console.log("List size before: " + petitions.list.length);
                            console.log("Size of next page: " + data["petitions"].length);
                        }
                    //    console.log('we '+ data["petitions"]);
                        let searchString = window.petitions.searchString;
                        petitions.list = [];
                        let list = data["petitions"].filter((item) =>
                                    item.title.toLowerCase().includes(searchString.toLowerCase())
                                    || item.title.toLowerCase().replace(/(~|`|!|@|#|$|%|^|&|\*|\(|\)|{|}|\[|\]|;|:|\"|'|<|,|\.|>|\?|\/|\\|\||-|_|\+|=)/g, "").includes(searchString.toLowerCase()))
                        petitions.list.push(...list);
                        setMapBasedOnLocation(list);
                        petitions.loading = false;
                        petitions.searched = false;

                        if (websocket_debug) console.log("List size after: " + petitions.list.length)

                    }
                    else if (websocket_debug) {
                        console.log("Unrecognized command: " + command);
                        console.log(data);
                    }

                }
                // else {

                //     // Default behaviour is to update everything on response if no command is given.
                //     if (data.hasOwnProperty("petitions")) {
                //         petitions.list = data["petitions"];
                //         petitions.map = data["map"];
                //         petitions.loading = false;
                //         petitionID = getUrl("p");
                //         if (petitionID) {
                //             openPetition(petitionID, true);
                //         }
                //     }
                //     else if (websocket_debug) {

                //         console.log("Default action failed; petitions object does not exist in response.");

                //     }

                // }

            }
            catch (error) {

                // Catch any errors and reset the petition data.
                console.error(error, data);
                updatePetitionHistory(false);

            }
        };
    }

    function reportPetitionModal(petition_id){
        window.popup = new Modal({
            headerClass: "highlight",
            headerContent: "<h2>Why are you reporting this petition?</h2>",
            bodyContent: "<select id='report-petition-select'><option value='Spam or misleading'>Spam or misleading</option><option value='Hateful or abusive'>Hateful or abusive</option><option value='Harassing or violent'>Harassing or violent</option><option value='Against policy'>Against policy</option></select><p>An email will be sent to moderators that will contain your initials and the reason you selected to report this petition.</p><p>Reporting a petition does not necessarily mean that it will be taken down. The petition will be reviewed by the current Student Government administration and a decision will be made.</p>",
            iconContainerClass:"text-highlight",
            iconClass:"md-48",
            iconText:"report",
            bodyButtons: [
                ["Report", "material material-button material-shadow margin-top margin-bottom transition", 'reportPetition('+petition_id+', $("#report-petition-select").val())'],
                ["Cancel", "material material-button material-shadow margin-top margin-bottom transition minimal", "window.popup.close()"]
            ]
        });
        popup.open();
    }

    function reportErrorModal(){
        window.errorModalInstance = new Modal({
            headerContent:"<h2>Error reporting petition</h2>",
            bodyContent:"You've already reported this petition.",
            iconContainerClass:"text-highlight",
            iconClass:"md-48",
            iconText:"error",
            bodyButtons: [
                ["Okay","material material-button minimal material-shadow margin-top margin-bottom transition","window.errorModalInstance.close()"]
            ]
        });
        errorModalInstance.open();
    }

    function reportPetition(petition_id, reason){
        var allowedReasons = ["Spam or misleading", "Hateful or abusive", "Against policy", "Harassing or violent"];
        if (allowedReasons.includes(reason)){
            $.post('petition/report/'+petition_id, {'reason': reason, "csrfmiddlewaretoken": get_csrf()}, (r) => {
                window.popup.close();
                if (!(JSON.parse(r))) {
                    reportErrorModal();
                }
            })
        }
    }

    $(document).ready(function(){

        window.page = 1;
        setupSocket();
        // petitionID = getUrl("p");
        // if(petitionID && modalData.petition.id !== Number(petitionID)){
        //     openPetition(petitionID, true);
        // }
        
        // Get the sort key globally
        var sort = $("#sort");
        let sort_by = 'most recent';
        var filter_tag = $("#mobile-filter").val()
        sort.on("click", function (params) {
            sort.is(":checked") ? (sort.prop("checked", false)) : sort.prop("checked", true);
            if (sort.is(":checked")) {
                console.log(sort);
                sort_by = 'most recent';
                sort.prop("checked", false);
            } else {
                sort_by = 'most signatures';
                sort.prop("checked", true);
                console.log('tru');
                console.log(sort.is(":checked"), 'trending');
            }
            // Grab the tag name
            
            // console.log(filter_tag, 'trending filter_tag');

            // Reload all of the petitions with the updated information.
            reloadPetitions(sort_by, filter_tag, socket);
        });

         $("#mobile-filter").change(function () {

            // Grab the tag name
            var filter_tag = $(this).val();
            sort_by = 'most recent';
            sort.prop("checked", false);

            // Reload all of the petitions with the updated information.
            reloadPetitions(sort_by, filter_tag, socket);

        });
        socket.onopen = ()=> {
            console.log('onopen 2 is a thing?');
            petitionID = getUrl("p");
            if(petitionID && modalData.petition.id !== Number(petitionID)){
                openPetition(petitionID, true);
            }
            loadPetitions(sort_by, filter_tag, socket);
        };
        // Bind parallax effects.
        $("#parallax-slideshow").parallax({divisor:-2.5});
        $("#parallax-overlay").parallax({divisor:-5,offset:30});
        $(".slideshow-container").slideshow();

        // Event Listeners.
        $(document).on("click", ".tag", function () {
            // Bind the click event on elements with the tag class

            // Get the tag name
            var filter_tag = $(this).data("tag");
            sort_by = 'most recent';
            sort.prop("checked", false);

            // Update the select field for mobile devices
            $("#mobile-filter").val(filter_tag);
            // console.log(filter_tag,'filter_tag');

            // Reload all of the petitions with the updated information.
            reloadPetitions(sort_by, filter_tag, socket);
            
            $('html, body').animate({scrollTop: $("#petitions").offset().top -100 }, 'slow');

        });

       

        $(document).on("click","#action-drawer-icon-container", function () {
            var me = $(this);
            var icon = me.find("i");
            var actionCards = $("#action-cards");
            if(icon.html() === "keyboard_arrow_down"){
                icon.html("keyboard_arrow_up");
                actionCards.data("closed",true);
            }
            else{
                icon.html("keyboard_arrow_down");
                actionCards.data("closed",false);
            }
            setContentAvailableSpace($("#petition-modal"),200); // Extend the petition modal box too much so the animation is smooth
            actionCards.toggle(200,"linear",function () {
                setContentAvailableSpace($("#petition-modal")); // Resize the box so it is the correct size.
            });
        });

        $(document).on("click","#sign-petition-button", function () {
            var petition = getUrl("p");
            petitions.list[petitions.map[petition]].isSigned = 1;
            $.post('/petition/sign/'+petition,{"csrfmiddlewaretoken":get_csrf()}, (r) => {
                if(r !== petition){
                    console.log("Sign Petition response: "+r);
                }
                if(modalData.petition.id === Number(petition)){

                    modalData.petition.isSigned = 1;

                }
            });
        });

        $(document).on("click","#report-petition-link", (e) => {
            e.preventDefault();
            var petition = getUrl("p");
            reportPetitionModal(petition);
        });

        $(document).on("click","#publish-button", function () {
            var petition = getUrl("p");

            window.popup = new Modal({
                headerContent:"<h2>Are you sure you want to publish this petition?</h2>",
                bodyContent:"<p class='padding-bottom'>You cannot edit or delete it once it is published.</p>",
                iconContainerClass:"text-highlight",
                iconClass:"md-48",
                iconText:"warning",
                bodyButtons: [
                    ["Cancel","material material-button minimal material-shadow margin-top margin-bottom transition","window.popup.close()"],
                    ["Confirm", "material material-button material-shadow margin-bottom margin-top transition cursor","publishPetition("+petition+")"]
                ]
            });
            popup.open();

        });

        var paginationTimeout = setTimeout(function () {},0);
        $(window).scroll(function () {
            var win = $(window);
            if(win.scrollTop() + win.height() > $(document).height() - 100){
                // Do not call paginate if the user has searched something.
                // Do not call paginate if Petitions are currently being loaded.
                // Only call paginate if the last paginate returned some petitions.
                if(!window.searched && !window.petitions.loading && (!window.last_paginate || (window.last_paginate && window.last_paginate.length !== 0))){

                    // Timeout will prevent duplicate calls to paginate
                    clearTimeout(paginationTimeout);
                    paginationTimeout = setTimeout(function () {
                        window.page++;
                        window.petitions.loading = true;
                         var filter_tag = $("#mobile-filter").val()
                        loadPetitions(sort_by, filter_tag, window.socket);
                    },250);

                }
            }



        });

        window.onpopstate = function () {
            //Refresh the page on back.
            location.reload();
        };

        // let petID = getUrl("p");
        // if (petID) openPetition(petID);

    });

    $(window).resize(function () {

        Waypoint.refreshAll();
        var actionCards = $("#action-cards");
        if($(window).width() > 830 && actionCards.data("closed")){
            // Open the action cards when the width of the window is over 830px and they are currently hidden.
            setContentAvailableSpace($("#petition-modal"),200); // Extend the petition modal box too much so the animation is smooth
            actionCards.show(200,"linear",function(){
                actionCards.data("closed",false);
                setContentAvailableSpace($("#petition-modal")); // Resize the box so it is the correct size.
            });
            $("#action-drawer-icon-container").find("i").html("keyboard_arrow_down"); // Update the icon so it
        }
        else{
            setContentAvailableSpace($("#petition-modal"));
        }

    });