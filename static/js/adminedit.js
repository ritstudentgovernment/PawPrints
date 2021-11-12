function adminEdit(action, id = false){
    /**
     * This function handles all things admin-edit related.
     *
     * Builds the editing modals and callbacks.
     **/
    function initTinyMCE(){
        tinymce.remove();
        return tinymce.init({
            selector: '#admin-edit',
            inline: false,
            menubar: false,
            plugins: "link paste",
            paste_auto_cleanup_on_paste : true,
            paste_remove_styles: true,
            paste_remove_styles_if_webkit: true,
            paste_strip_class_attributes: "all",
            height: 300,
            toolbar: "insert | undo redo | styleselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link removeformat",
            init_instance_callback: function (editor) {
                editor.on('Change', function (e) {
                    var value = e.level.content.trim();
                    e.level.content = value.replace(/<\/?g[^>]*>/g, "");
                });
            }
        });
    }
    switch(action){
        case "update":
            // Build the update modal
            window.updateModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Add Update</h2>",
                bodyContent:"<div id='admin-edit'>Write your update here.</div> <h5> Note: Once you submit this update you may not change it. </h5>",
                bodyButtons:[
                    ["Cancel","material-button material-hover material-shadow cursor transition minimal","window.updateModal.close()"],
                    ["Submit","material-button material-hover material-shadow cursor transition",'update("add_update",tinymce.get("admin-edit").getContent(),getUrl("p"),function(r){window.updateModal.close();})']
                ],
                closeCallback: function(){
                    tinymce.remove("#admin-edit");
                }
            });
            updateModal.open();
            initTinyMCE();
            setTimeout(function(){
                updateModal.positionModal();
            },0);
            return true;
        case "respond":
            // Build the response modal
            var response = window.modalData.petition.response;
            response = response === undefined ? "Write your response here." : response;
            window.responseModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Respond to this petition</h2>",
                bodyContent:"<div id='admin-edit'>"+response+"</div>",
                bodyButtons:[
                    ["Cancel","material-button material-hover material-shadow cursor transition minimal","window.responseModal.close()"],
                    ["Submit","material-button material-hover material-shadow cursor transition",'update("response",tinymce.get("admin-edit").getContent(),getUrl("p"),function(r){window.responseModal.close();})']
                ],
                closeCallback: function(){
                    tinymce.remove("#admin-edit");
                }
            });
            responseModal.open();
            initTinyMCE();
            setTimeout(function(){
                responseModal.positionModal();
            },0);
            return true;
        case "delete":
            // Build the Deletion modal
            window.deleteModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Un-publish this petition.</h2>",
                bodyContent:"<p>WARNING! There is no going back once you remove this petition.</p>",
                bodyButtons:[
                    ["Cancel","material-button material-hover material-shadow cursor transition minimal","window.deleteModal.close()"],
                    ["Submit","material-button material-hover material-shadow cursor transition",'update("unpublish",false,getUrl("p"),function(r){window.deleteModal.close();$("#petitions-container").find("[data-petition-id="+getUrl("p")+"]").remove();window.modalData.closePetition();})']
                ]
            });
            deleteModal.open();
            return true;
        case "mark_in_progress":
            // Build the Deletion modal
            window.chargeModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Charge This Petition.</h2>",
                bodyContent:"<p>Choose a committee to assign this petition to.</p>",
                bodyButtons:[
                    ["Academics & Co-ops","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Academics & Co-Ops")'],
                    ["Housing & Dining","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Dining")'],
                    ["Facilities, Parking, & Transportation","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Facilities & Parking")'],
                    ["Student Affairs","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Student Affairs")'],
                    ["Sustainability","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Sustainability")'],
                    ["Deaf Advocacy","material-button material-hover material-shadow cursor transition minimal",'setCommitteeTag("Deaf Advocacy")']
                ]
            });
            chargeModal.open();
            return true;
        case "edit-update":
            if(window.debug)console.log("EDIT UPDATE "+id);
            window.edit_update_position = id;
            window.editUpdateModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Edit this update</h2>",
                bodyContent:"<div id='admin-edit'>"+modalData.timeline[id].content+"</div>",
                bodyButtons:[
                    ["Cancel","material-button material-hover material-shadow cursor transition minimal","window.editUpdateModal.close()"],
                    ["Submit","material-button material-hover material-shadow cursor transition",
                        'update(' +
                        '"editUpdate",' +
                        'JSON.stringify({"update":tinymce.get("admin-edit").getContent(),"position":window.edit_update_position}),' +
                        'getUrl("p"),' +
                        'function(r){if(window.debug)console.log(r);window.editUpdateModal.close();window.modalData.closePetition();})']
                ]
            });
            editUpdateModal.open();
            initTinyMCE();
            setTimeout(function(){
                editUpdateModal.positionModal();
            },0);
            return true;
        case "edit-response":
            window.editResponseModal = new Modal({
                icon: false,
                headerClass:"background-highlight bright-text",
                headerContent: "<h2>Edit this response</h2>",
                bodyContent:"<div id='admin-edit'>"+modalData.timeline[id].content+"</div>",
                bodyButtons:[
                    ["Cancel","material-button material-hover material-shadow cursor transition minimal","window.editResponseModal.close()"],
                    ["Submit","material-button material-hover material-shadow cursor transition",
                        'update(' +
                        '"editResponse",' +
                        'tinymce.get("admin-edit").getContent(),' +
                        'getUrl("p"),' +
                        'function(r){if(window.debug)console.log(r);window.editResponseModal.close();window.modalData.closePetition();})']
                ]
            });
            editResponseModal.open();
            initTinyMCE();
            setTimeout(function(){
                editResponseModal.positionModal();
            },0);
            return true;
        default:
            throw "Error when dispatching an admin control action.";
    }
}
function setCommitteeTag(targetTag) {
    update("mark-in-progress", false, getUrl("p"));
    update("committee", targetTag, getUrl("p"));
    window.chargeModal.close();
}
$(document).on("click","#admin-actions .circle",function(e){
    if(window.debug)console.log("CLICK ADMIN BUTTON");
    var clicked = $(e.target).closest(".circle");
    var action = clicked.data("admin-control");
    adminEdit(action);
});
$(document).on("click",".admin-edit-icon",function(e){
    if(window.debug)console.log("CLICK ADMIN BUTTON");
    var clicked = $(e.target).closest(".timeline-element");
    var clicked_type = clicked.data("type").toLowerCase().replace(/(sg|official)/g,'').trim();
    var element_id = clicked.data("element");
    var action = "edit-"+clicked_type;
    adminEdit(action, element_id);
});
