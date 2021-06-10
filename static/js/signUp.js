// {% if msg %}
//     alert("{{ msg }}")
// {% endif %}
// {#회원가입 !!!! #}

function sign_up() {
    let username = $("#input-username").val()
    let nickname = $("#input-nickname").val()
    let password = $("#input-password").val()
    let password2 = $("#input-password2").val()
    console.log(username, password, password2)

    //{# help-id가 is-danger 클래스 갖고 있으면 중복검사 통과 못한거니까 아이디 다시 확인해라#}
    if ($("#help-id").hasClass("is-danger")) {
        alert("아이디를 다시 확인해주세요.")
        return;
        //{# help-id가 is-success 클래스 갖고 있지 않으면 중복검사 해라#}
    } else if (!$("#help-id").hasClass("is-success")) {
        alert("아이디 중복확인을 해주세요.")
        return;
    }
    if (nickname == "") {
        $("#help-nickname").text("닉네임을 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-nickname").focus()
        return;
    } else if (!is_nickname(nickname)) {
        $("#help-nickname").text("닉네임의 형식을 확인해주세요. 한글, 영문, 숫자 사용 가능하며 2자 이상").removeClass("is-safe").addClass("is-danger")
        $("#input-nickname").focus()
        return;
    } else {
        $("#help-nickname").text("사용할 수 있는 닉네임입니다.").removeClass("is-danger").addClass("is-success")
    }
    if (password == "") {
        $("#help-password").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return;
    } else if (!is_password(password)) {
        $("#help-password").text("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return;
    } else {
        $("#help-password").text("사용할 수 있는 비밀번호입니다.").removeClass("is-danger").addClass("is-success")
    }
    if (password2 == "") {
        $("#help-password2").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else if (password2 != password) {
        $("#help-password2").text("비밀번호가 일치하지 않습니다.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else {
        $("#help-password2").text("비밀번호가 일치합니다.").removeClass("is-danger").addClass("is-success")
    }
    $.ajax({
        type: "POST",
        url: "/sign_up/save",
        data: {
            id: username,
            pw: password,
            nickname: nickname
        },
        success: function (response) {
            alert("회원가입을 축하드립니다!")
            window.location.replace("/login")
        }
    });
}

// {# 아이디, 비밀번호 정규식!! #}

function is_username(asValue) {
    //{# 괄호 ( )안의 요소는 필수 포함 요소임. a-zA-Z 소문자 a-z, 대문자 A-Z 포함! 대괄호는 선택포함을 의미함. 숫자 0-9사용가능!. 2-10자여야 한다!#}
    var regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
    return regExp.test(asValue);
}

function is_nickname(asValue) {
    var regExp = /^[가-힣ㄱ-ㅎa-zA-Z0-9._-]{2,}$/;
    return regExp.test(asValue);
}

function is_password(asValue) {
    // {# *\d = 숫자 무조건 포함해라#}
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

// {# 아이디 중복확인 !!! #}

function check_dup() {
    let username = $("#input-username").val()
    if (username == "") {
        $("#help-id").text("아이디를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()
        return;
    }
    if (!is_username(username)) {
        $("#help-id").text("아이디의 형식을 확인해주세요. 영문과 숫자, 일부 특수문자(._-) 사용 가능. 2-10자 길이").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()
        return;
    }
    $("#help-id").addClass("is-loading")
    $.ajax({
        type: "POST",
        url: "/sign_up/checkDup",
        data: {
            id: username
        },
        success: function (response) {
            if (response["exists"]) {
                $("#help-id").text("이미 존재하는 아이디입니다.").removeClass("is-safe").addClass("is-danger")
                $("#input-username").focus()
            } else {
                $("#help-id").text("사용할 수 있는 아이디입니다.").removeClass("is-danger").addClass("is-success")
            }
            $("#help-id").removeClass("is-loading")
        }
    });
}

// {# 닉네임 중복확인 !!! #}

function nik_check_dup() {
    let nickname = $("#input-nickname").val()
    if (nickname == "") {
        $("#help-nickname").text("닉네임을 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-nickname").focus()
        return;
    }
    if (!is_nickname(nickname)) {
        $("#help-nickname").text("아이디의 형식을 확인해주세요. 영문과 숫자, 일부 특수문자(._-) 사용 가능. 2-10자 길이").removeClass("is-safe").addClass("is-danger")
        $("#input-nickname").focus()
        return;
    }
    $("#help-nickname").addClass("is-loading")
    $.ajax({
        type: "POST",
        url: "/sign_up/nik_checkDup",
        data: {
            nickname: nickname
        },
        success: function (response) {
            if (response["exists"]) {
                $("#help-nickname").text("이미 존재하는 닉네임입니다.").removeClass("is-safe").addClass("is-danger")
                $("#input-nickname").focus()
            } else {
                $("#help-nickname").text("사용할 수 있는 닉네임입니다.").removeClass("is-danger").addClass("is-success")
            }
            $("#help-nickname").removeClass("is-loading")
        }
    });
}