const btnlogin = document.getElementById("sign-in-login"),
      btnregistar = document.getElementById("sign-up-login"),
      contenedorregistro = document.querySelector(".register-register"),
      contenedorlogin = document.querySelector(".login-login");

btnlogin.addEventListener("click", e => {
    contenedorregistro.classList.add("hide2");
    contenedorlogin.classList.remove("hide2");
})


btnregistar.addEventListener("click", e => {
    contenedorlogin.classList.add("hide2");
    contenedorregistro.classList.remove("hide2")
})
