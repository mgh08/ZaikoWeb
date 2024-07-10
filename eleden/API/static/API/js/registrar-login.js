/*js login register*/

const btnSignIn = document.getElementById("sign-in"),
      btnSignUp = document.getElementById("sign-up"),
      containerFormRegister = document.querySelector(".register"),
      containerFormText = document.querySelector(".text-demo"),
      containerFormLogin = document.querySelector(".login");
      

btnSignIn.addEventListener("click", e => {
    containerFormRegister.classList.add("hide");
    containerFormLogin.classList.remove("hide");
    containerFormText.classList.add("hide");
})


btnSignUp.addEventListener("click", e => {
    containerFormLogin.classList.add("hide");
    containerFormRegister.classList.remove("hide");
    containerFormText.classList.remove("hide");
})





