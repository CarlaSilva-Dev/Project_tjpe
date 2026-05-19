/* =========================================================
   DASHBOARD.JS — SISTEMA TJPE
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SIDEBAR — COLAPSAR / EXPANDIR
    ====================================================== */
    const menuBtn   = document.getElementById("menu-btn");
    const sidebar   = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");

    // Restaura estado salvo
    const savedState = localStorage.getItem("sidebarCollapsed");
    if (savedState === "true") {
        sidebar.classList.add("collapsed");
        mainContent.classList.add("expanded");
    }

    if (menuBtn && sidebar) {
        menuBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            const isCollapsed = sidebar.classList.toggle("collapsed");
            mainContent.classList.toggle("expanded", isCollapsed);
            localStorage.setItem("sidebarCollapsed", isCollapsed);
        });
    }

    // Mobile: fechar ao clicar fora
    document.addEventListener("click", function (e) {
        if (!sidebar || !menuBtn) return;
        const isMobile = window.innerWidth <= 768;
        if (isMobile &&
            !sidebar.contains(e.target) &&
            !menuBtn.contains(e.target)) {
            sidebar.classList.remove("active");
        }
    });

    // Mobile: menu hamburguer abre/fecha sidebar
    if (menuBtn) {
        menuBtn.addEventListener("click", function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle("active");
            }
        });
    }


    /* =====================================================
       RELÓGIO
    ====================================================== */
    const relogio = document.getElementById("relogio");
    if (relogio) {
        const atualizar = () => {
            relogio.textContent = new Date().toLocaleString("pt-BR", {
                weekday: "long", day: "2-digit", month: "long",
                year: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"
            });
        };
        atualizar();
        setInterval(atualizar, 1000);
    }

    /* =====================================================
       ALERTAS — FECHAR AUTOMATICAMENTE
    ====================================================== */
    setTimeout(() => {
        document.querySelectorAll(".alert").forEach(a => {
            a.style.transition = "opacity .4s";
            a.style.opacity = "0";
            setTimeout(() => a.remove(), 400);
        });
    }, 5000);

    /* =====================================================
       CONFIRMAR EXCLUSÃO
    ====================================================== */
    document.querySelectorAll(".btn-excluir, [data-confirm]").forEach(btn => {
        btn.addEventListener("click", function (e) {
            const msg = this.dataset.confirm || "Deseja realmente excluir este registro?";
            if (!confirm(msg)) e.preventDefault();
        });
    });

    /* =====================================================
       VALIDAÇÃO EMAIL EM TEMPO REAL
    ====================================================== */
    const emailInput = document.querySelector("input[type='email']");
    if (emailInput) {
        emailInput.addEventListener("blur", function () {
            const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
            this.classList.toggle("input-error",   !ok);
            this.classList.toggle("input-success",  ok);
        });
    }

    /* =====================================================
       FORÇA DE SENHA
    ====================================================== */
    const senhaInput = document.querySelector("#senha");
    if (senhaInput) {
        senhaInput.addEventListener("keyup", function () {
            const forte = this.value.length >= 6 &&
                /\d/.test(this.value) &&
                /[a-zA-Z]/.test(this.value);
            this.classList.toggle("input-error",  !forte && this.value.length > 0);
            this.classList.toggle("input-success",  forte);
        });
    }

    /* =====================================================
       MÁSCARA CPF
    ====================================================== */
    document.querySelectorAll("#cpf_autor, input[name='cpf']").forEach(el => {
        el.addEventListener("input", function () {
            let v = this.value.replace(/\D/g, "").slice(0, 11);
            v = v.replace(/(\d{3})(\d)/, "$1.$2");
            v = v.replace(/(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
            v = v.replace(/(\d{3})\.(\d{3})\.(\d{3})(\d{1,2})$/, "$1.$2.$3-$4");
            this.value = v;
        });
    });

    /* =====================================================
       MÁSCARA NÚMERO PROCESSO CNJ
    ====================================================== */
    const numProc = document.querySelector("input[name='numero']");
    if (numProc) {
        numProc.addEventListener("input", function () {
            let v = this.value.replace(/\D/g, "").slice(0, 20);
            if (v.length > 7)  v = v.slice(0,7)  + "-" + v.slice(7);
            if (v.length > 10) v = v.slice(0,10) + "." + v.slice(10);
            if (v.length > 15) v = v.slice(0,15) + "." + v.slice(15);
            if (v.length > 17) v = v.slice(0,17) + "." + v.slice(17);
            if (v.length > 19) v = v.slice(0,19) + "." + v.slice(19);
            this.value = v;
        });
    }

    /* =====================================================
       BUSCA LOCAL NA TABELA
    ====================================================== */
    const filtroTabela = document.getElementById("filtroTabela");
    if (filtroTabela) {
        filtroTabela.addEventListener("keyup", function () {
            const val = this.value.toLowerCase();
            document.querySelectorAll("table tbody tr").forEach(tr => {
                tr.style.display = tr.innerText.toLowerCase().includes(val) ? "" : "none";
            });
        });
    }

    /* =====================================================
       MOSTRAR / OCULTAR SENHA (login)
    ====================================================== */
    const toggleSenha = document.getElementById("toggleSenha");
    if (toggleSenha && senhaInput) {
        toggleSenha.addEventListener("click", function () {
            const show = senhaInput.type === "password";
            senhaInput.type = show ? "text" : "password";
            this.innerHTML = show
                ? '<i class="fa fa-eye-slash"></i>'
                : '<i class="fa fa-eye"></i>';
        });
    }

    /* =====================================================
       ANIMAÇÃO CARDS (fade-in escalonado)
    ====================================================== */
    document.querySelectorAll(".card-box, .card-kpi").forEach((el, i) => {
        el.style.opacity = "0";
        el.style.transform = "translateY(12px)";
        setTimeout(() => {
            el.style.transition = "opacity .35s ease, transform .35s ease";
            el.style.opacity = "1";
            el.style.transform = "none";
        }, i * 60);
    });

    /* =====================================================
       DATATABLE (aplicado automaticamente a tabelas marcadas)
    ====================================================== */
    if (typeof DataTable !== "undefined") {
        document.querySelectorAll("table.dt-auto").forEach(tbl => {
            new DataTable(tbl, {
                pageLength: 10,
                language: {
                    search: "Pesquisar:",
                    lengthMenu: "Mostrar _MENU_ registros",
                    info: "_START_–_END_ de _TOTAL_",
                    paginate: { first:"Primeiro", last:"Último", next:"Próximo", previous:"Anterior" },
                    zeroRecords: "Nenhum registro encontrado"
                }
            });
        });
    }

    console.log("✔ Sistema TJPE carregado com sucesso.");
});