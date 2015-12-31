function jQueryEscapeStr(str) {
    if (str)
        return str.replace(/([ #;?%&,.+*~\':"!^$[\]()=>|\/@])/g,'\\$1');      

    return str;
}
function show_iframe() {
    $('#modal-progress-bar').css('display', 'none');
    $('#modal-iframe-div').css('display', '');
    
    var iframe = document.getElementById('modal-iframe');
    iframe.height = iframe.contentWindow.document.body.scrollHeight + "px";
}
function openModalFrame(modalTitle, url) {
    $('.modal-title').text(modalTitle);
    $('#modal').modal({show: true}).on('hidden.bs.modal', function(e) {
        modalClosed();
    });

    var replacementHTML = '<div id="modal-iframe-div" style="display: none"><iframe id="modal-iframe" width="100%" frameborder="0" src="' + url + '"></iframe></div>';
    $('#modal-body').append(replacementHTML);
    document.getElementById('modal-iframe').onload = function() {
        show_iframe();
    };
}
function modalClosed() {
    $('#modal-iframe-div').remove();
    $('#modal-progress-bar').css('display', '');
}