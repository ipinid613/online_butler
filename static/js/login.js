function login() {
    let id = $('#id').val()
    let pw = $('#pw').val()

    $.ajax({
        type: "POST",
        url: "/",
        data: {
            id: id,
            pw: pw
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.replace("/home")
                alert(response['msg'])
            } else if (id === '' || pw === '') {
                alert('아이디 또는 비밀번호를 입력해주세요')
            } else {
                alert(response['msg'])
            }
        }
    })
}