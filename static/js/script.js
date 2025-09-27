document.getElementById("btnMenu").addEventListener("click",
    function () {
      
      let elemento = document.getElementById("navbar");
      if (elemento.classList.contains("navbar")) {
        elemento.classList.remove("navbar");
        elemento.classList.add("no_navbar");
    }   else {
        elemento.classList.remove("no_navbar");
        elemento.classList.add("navbar");
    }

    });