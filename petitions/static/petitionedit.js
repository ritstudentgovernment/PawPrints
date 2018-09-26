function verifyInputs(){
    var allPass = true;
    var message = "";
    $(".verify").each(function(){
        var thisPass = true;
        var input = $(this);
        var value;
        if(input.hasClass("editable")){
            value = tinyMCE.get(input.attr("id")).getContent();
            if(value.trim() === "" || ( value.indexOf("{{ default_title }}") > -1 ) || ( value.indexOf("{{ default_body }}") > -1 ) ){
                allPass = thisPass = false;
                input.addClass("error");
            }
            else if(input.data("limit-length") && value.length > 80 ){
                allPass = false;
                message += "Your petition title may not be longer than 80 characters.\n";
                input.addClass("error");
            }
        }
        else{
            value = input.val();
            if(value.length === 0){
                allPass = thisPass = false;
                input.addClass("error");
            }
        }
        if(!thisPass){
            var failMessage = input.data("verify-fail-message");
            message += failMessage + "\n";
        }
    });
    return allPass ? allPass : message;
}
function errorModal(message){
    window.errorModalInstance = new Modal({
        headerContent:"<h2>There is an error in your petition content.</h2>",
        bodyContent:message,
        iconContainerClass:"text-highlight",
        iconClass:"md-48",
        iconText:"error",
        bodyButtons: [
            ["Okay","material material-button minimal material-shadow margin-top margin-bottom transition","window.errorModalInstance.close()"]
        ]
    });
    errorModalInstance.open();
}
function unescape(string){
    /**
     * This function unescapes certain characters sent in the JSON response for each petition so they show up correctly.
     **/
    return string.replace(/\\"/g,"'")
        .replace(/\"/g,'')
        .replace(/&lt;/g,"<")
        .replace(/&gt;/g,">")
        .replace(/&amp;/g,"&")
        .replace(/nbps;/g," ")
        .replace(/"/g,"")
        .replace(/\\n/g, "\n")
        .replace(/(\\u201c|\\u201d)/g,'\"')
        .replace(/\\u2014/g,'&mdash;')
        .replace(/(\\u2019|\\u2018)/g,"'");
}
$(document).ready(function(){
    tinymce.init({
        selector: '#petition_description',
        inline: false,
        height: 230,
        menubar: false,
        plugins: "image link paste",
        paste_auto_cleanup_on_paste : true,
        paste_remove_styles: true,
        paste_remove_styles_if_webkit: true,
        paste_strip_class_attributes: "all",
        toolbar: "insert | undo redo | styleselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link removeformat",
        init_instance_callback: function (editor) {
            editor.on('Change', function (e) {
                var value = e.level.content.trim();
                value = value.replace(/<\/?g[^>]*>/g, "");
                if(value !== ""){
                    update("description",value,petition_id);
                }
            });
        }
    });
    tinymce.init({
        selector: '#petition_title',
        inline: true,
        menubar: false,
        toolbar: false,
        init_instance_callback: function (editor) {
            editor.on('Change', function (e) {
                var value = ucfirst(e.level.content.trim().replace(/<\/?[^>]+(>|$)/g, ""));
                if(value.length > 80){
                    errorModal("Your petition title may not be longer than 80 characters.");
                }
                else{
                    if(value !== ""){
                        update("title",value,petition_id);
                    }
                }
            });
        }
    });

    $('#tags-select').select2({
        placeholder: "Petition Tags",
        width: "resolve",
        maximumSelectionLength: 3,
        noResults: function(){return "No tags found."},
        formatSelectionTooBig: "You can only select up to 3 tags."
    });
    var desc = $("#petition_description");
    var html = desc.html();
    desc.html(unescape(html));

});
var tags = $('#tags-select');
tags.on('select2:select', function (e) {
    var data = e.params.data;
    var id = data.id;
    update("add-tag",id,petition_id);
});
tags.on('select2:unselect', function (e) {
    var data = e.params.data;
    var id = data.id;
    update("remove-tag",id,petition_id);
});
$(document).on("click","#publish",function(){

    var verified = verifyInputs();
    if(verified === true){

        window.popup = new Modal({
            headerContent:"<h2>Are you sure you want to publish this petition?</h2>",
            bodyContent:"<p class='padding-bottom'>You cannot edit or delete it once it is published.</p>",
            iconContainerClass:"text-highlight",
            iconClass:"md-48",
            iconText:"warning",
            bodyButtons: [
                ["Cancel","material material-button minimal material-shadow margin-top margin-bottom transition","window.popup.close()"],
                ["Confirm", "material material-button material-shadow margin-bottom margin-top transition cursor","publishPetition("+petition_id+")"]
            ]
        });
        popup.open();

    }
    else{

        errorModal(verified);

    }

});