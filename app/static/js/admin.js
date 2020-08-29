//JS For manage-articles when select articles or select comments
$(document).ready(function () {
    $('#select-all').click(function () {
        if ($(this).prop('checked')) {
            $('.op_check').prop('checked', true);
        } else {
            $('.op_check').prop('checked', false);
        }
    });
});

//JS For submit article id to delete article
function delCfm(articleId) {
    $('#cfmClick').click(function () {
        formSubmit(articleId);
    });
    $('#delCfmModel').modal();
}
function formSubmit(articleId) {
    $('#delForm' + articleId).submit();
}

//JS For select articles to delete
$(document).ready(function () {
    $('#delArtsCfm').click(function(){
        $('#delArticlesForm').submit();
    });

    $('#delArticles').click(function () {
        if ($('.op_check').filter(':checked').size() > 0) {
            var articleIds = [];
            $('.op_check:checked').each(function(){
                articleIds.push($(this).val());
            });
            var articleIdsJson = JSON.stringify(articleIds);
            $('#articleIds').val(articleIdsJson);
            $('#delArtsCfmModel').modal();
        } else {
            $('#selArtsCfmModel').modal();
        }
    });
});

//JS For confirm to delete a plugin
function delPluginCfm(url) {
    $('#delPluginCfmClick').click(function(){
        window.location.href = url;
    });
    $('#delPluginCfmModal').modal();
}

//JS For change password
function changePassword() {
    $('#changePasswordFormModal').modal();
}

//JS For edit user info
function EditUserInfo() {
    $('#editUserInfoFormModal').modal();
}

//JS For upload new Gravatar
function uploadGravatar() {
    $('#changeGravatarFormModal').modal();
}

function sendEmail() {
    $('#sendEmailFormModal').modal();
}
