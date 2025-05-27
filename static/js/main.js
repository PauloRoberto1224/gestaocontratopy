/**
 * Função para inicializar os tooltips do Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Função para inicializar os popovers do Bootstrap
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Função para inicializar as tabelas com DataTables
 */
function initDataTables() {
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Portuguese-Brasil.json'
            },
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            pageLength: 10,
            lengthMenu: [5, 10, 25, 50, 100],
            order: [[0, 'desc']]
        });
    }
}

/**
 * Função para inicializar os selects estilizados
 */
function initSelect2() {
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'Selecione uma opção',
            allowClear: true,
            language: 'pt-BR'
        });
    }
}

/**
 * Função para inicializar os datepickers
 */
function initDatepickers() {
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'dd/mm/yyyy',
            language: 'pt-BR',
            autoclose: true,
            todayHighlight: true
        });
    }
}

/**
 * Função para inicializar os inputs de máscara
 */
function initMasks() {
    if ($.fn.mask) {
        $('.cpf-mask').mask('000.000.000-00', {reverse: true});
        $('.cnpj-mask').mask('00.000.000/0000-00', {reverse: true});
        $('.phone-mask').mask('(00) 00000-0000');
        $('.money-mask').mask('000.000.000.000.000,00', {reverse: true});
        $('.cep-mask').mask('00000-000');
    }
}

/**
 * Função para confirmar exclusão
 */
function confirmDelete(event) {
    event.preventDefault();
    const deleteUrl = event.currentTarget.getAttribute('href');
    
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Esta ação não pode ser desfeita!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = deleteUrl;
        }
    });
}

/**
 * Função para copiar texto para a área de transferência
 * @param {string} text - Texto a ser copiado
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Mostrar mensagem de sucesso
        const toast = new bootstrap.Toast(document.getElementById('copyToast'));
        const toastBody = document.querySelector('#copyToast .toast-body');
        toastBody.textContent = 'Texto copiado para a área de transferência!';
        toast.show();
    }).catch(err => {
        console.error('Erro ao copiar texto: ', err);
    });
}

/**
 * Função para alternar entre temas claro/escuro
 */
function toggleTheme() {
    const html = document.documentElement;
    const theme = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Atualizar ícone do botão
    const themeIcon = document.querySelector('.theme-toggle i');
    if (theme === 'dark') {
        themeIcon.classList.remove('bi-moon');
        themeIcon.classList.add('bi-sun');
    } else {
        themeIcon.classList.remove('bi-sun');
        themeIcon.classList.add('bi-moon');
    }
}

// Inicialização quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initTooltips();
    initPopovers();
    initDataTables();
    initSelect2();
    initDatepickers();
    initMasks();
    
    // Configurar botões de exclusão
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', confirmDelete);
    });
    
    // Configurar botão de alternar tema
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        
        // Verificar tema salvo
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        
        // Atualizar ícone do botão
        const themeIcon = themeToggle.querySelector('i');
        if (savedTheme === 'dark') {
            themeIcon.classList.remove('bi-moon');
            themeIcon.classList.add('bi-sun');
        }
    }
    
    // Atualizar data e hora no rodapé
    const currentYear = new Date().getFullYear();
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = currentYear;
    }
    
    // Adicionar classe de animação para elementos com atraso
    setTimeout(() => {
        document.querySelectorAll('.fade-in-delay').forEach((el, index) => {
            setTimeout(() => {
                el.classList.add('fade-in');
            }, 100 * index);
        });
    }, 300);
});

// Função para exibir mensagens de erro de formulário
function displayFormErrors(form, errors) {
    // Limpar erros anteriores
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Exibir novos erros
    $.each(errors, function(field, messages) {
        const input = form.find(`[name="${field}"]`);
        input.addClass('is-invalid');
        
        let errorHtml = '<div class="invalid-feedback">';
        messages.forEach(function(message) {
            errorHtml += `<div>${message}</div>`;
        });
        errorHtml += '</div>';
        
        input.after(errorHtml);
    });
}

// Função para carregar dados via AJAX
function loadContent(url, container, callback) {
    $(container).addClass('loading');
    
    $.ajax({
        url: url,
        method: 'GET',
        success: function(response) {
            $(container).html(response);
            if (typeof callback === 'function') {
                callback();
            }
        },
        error: function(xhr) {
            console.error('Erro ao carregar conteúdo:', xhr);
            $(container).html('<div class="alert alert-danger">Erro ao carregar o conteúdo. Por favor, tente novamente.</div>');
        },
        complete: function() {
            $(container).removeClass('loading');
        }
    });
}

// Adicionar classe de carregamento aos botões de submit
$(document).on('submit', 'form', function() {
    const submitBtn = $(this).find('button[type="submit"]');
    submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processando...');
});
