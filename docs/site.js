/* Efeitos locais. Nada daqui sai do navegador: sem cookies, sem envio de dados. */
(function () {
  "use strict";

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  function ler(tipo, chave) {
    try { return window[tipo].getItem(chave); } catch (e) { return null; }
  }

  function gravar(tipo, chave, valor) {
    try { window[tipo].setItem(chave, valor); } catch (e) { /* sem armazenamento, segue a vida */ }
  }

  // Uma visita por sessão do navegador. Guarda o horário da visita anterior.
  var visitas = parseInt(ler("localStorage", "pv_visitas") || "0", 10) || 0;
  var anterior = ler("sessionStorage", "pv_anterior");
  if (ler("sessionStorage", "pv_sessao") === null) {
    anterior = ler("localStorage", "pv_ultima") || "";
    visitas += 1;
    gravar("localStorage", "pv_visitas", String(visitas));
    gravar("localStorage", "pv_ultima", String(Date.now()));
    gravar("sessionStorage", "pv_sessao", "1");
    gravar("sessionStorage", "pv_anterior", anterior);
  }

  var linha = document.getElementById("ultimo-registro");
  if (linha && visitas >= 5 && anterior) {
    var d = new Date(parseInt(anterior, 10));
    if (!isNaN(d.getTime())) {
      linha.textContent = "último registro: " + pad(d.getDate()) + "/" + pad(d.getMonth() + 1) +
        ", " + pad(d.getHours()) + ":" + pad(d.getMinutes());
      linha.hidden = false;
    }
  }

  function nevoa() {
    var raiz = document.documentElement;
    if (new Date().getHours() === 3) {
      raiz.classList.add("nevoa");
    } else {
      raiz.classList.remove("nevoa");
    }
  }
  nevoa();
  setInterval(nevoa, 60000);
})();
