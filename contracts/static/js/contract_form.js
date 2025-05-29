// Funções de formatação
function formatCurrencyOnBlur(input) {
    // Remove todos os caracteres não numéricos
    let value = input.value.replace(/[^\d,]/g, '');
    
    // Se não tiver vírgula, adiciona ,00
    if (value.indexOf(',') === -1 && value.length > 0) {
        value += ',00';
    }
    
    // Formata com pontos para milhares e mantém 2 casas decimais
    const parts = value.split(',');
    let intPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const decPart = parts[1] ? parts[1].substring(0, 2) : '00';
    
    // Atualiza o valor formatado
    input.value = intPart + (parts.length > 1 ? ',' + decPart : '');
}

function formatFiscalRegistration(input) {
    // Remove todos os caracteres não numéricos
    let value = input.val().replace(/[^\d]/g, '');
    
    // Formata CPF: 000.000.000-00
    if (value.length <= 11) {
        value = value.replace(/(\d{3})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d)/, "$1.$2");
        value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    } 
    // Formata CNPJ: 00.000.000/0000-00
    else {
        value = value.replace(/^(\d{2})(\d)/, "$1.$2");
        value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
        value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
        value = value.replace(/(\d{4})(\d)/, "$1-$2");
    }
    
    // Atualiza o valor formatado
    input.val(value);
}

function formatContractNumber(input) {
    let value = input.value.replace(/[^a-zA-Z0-9-]/g, '').toUpperCase();
    if (value.length > 20) {
        value = value.substring(0, 20);
    }
    input.value = value;
}

function formatCurrency(input) {
    const $field = $(input);
    let value = $field.val().replace(/[^\d,]/g, '');
    
    if (value.indexOf(',') === -1 && value.length > 0) {
        value += ',00';
    }
    
    const parts = value.split(',');
    let intPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    const decPart = parts[1] ? parts[1].substring(0, 2) : '00';
    
    if (value.length < $field.data('previous-length')) {
        $field.data('previous-length', value.length);
        return;
    }
    
    $field.val(intPart + (parts.length > 1 ? ',' + decPart : ''));
    $field.data('previous-length', $field.val().length);
}

// Funções de validação
function validateCPF(cpf) {
    if (!cpf) return false;
    cpf = cpf.replace(/[\D]/g, '');
    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;
    
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = 11 - (sum % 11);
    let digit = remainder >= 10 ? 0 : remainder;
    
    if (digit !== parseInt(cpf.charAt(9))) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
        sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = 11 - (sum % 11);
    digit = remainder >= 10 ? 0 : remainder;
    
    return digit === parseInt(cpf.charAt(10));
}

// Função para inicializar o formulário
function initializeForm() {
    // Inicializa os datepickers
    $('.datepicker').datepicker({
        dateFormat: 'dd/mm/yy',
        dayNames: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
        dayNamesMin: ['D', 'S', 'T', 'Q', 'Q', 'S', 'S', 'D'],
        dayNamesShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
        monthNamesShort: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        nextText: 'Próximo',
        prevText: 'Anterior',
        showOtherMonths: true,
        changeMonth: true,
        changeYear: true,
        yearRange: '1900:+0'
    });

    // Configura a máscara para campos de CPF/CNPJ
    $('.cpf-cnpj').on('input', function() {
        formatFiscalRegistration($(this));
    });

    // Configura a máscara para campos monetários
    $('.currency').on('blur', function() {
        formatCurrencyOnBlur(this);
    });

    // Configura a validação do formulário
    const form = document.getElementById('contractForm');
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    }, false);

    // Configura o preview de imagens para uploads
    $('input[type="file"]').on('change', function() {
        const input = this;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            const $preview = $(this).closest('.file-upload-container').find('.file-preview');
            
            reader.onload = function(e) {
                if (input.files[0].type.match('image.*')) {
                    $preview.html(`
                        <img src="${e.target.result}" class="img-fluid mb-2" alt="Preview">
                        <div class="file-info">
                            <p class="mb-0">${input.files[0].name}</p>
                            <small>${(input.files[0].size / 1024).toFixed(2)} KB</small>
                        </div>
                    `);
                } else {
                    $preview.html(`
                        <div class="file-info">
                            <i class="bi bi-file-earmark-text fs-1 text-muted"></i>
                            <p class="mb-0">${input.files[0].name}</p>
                            <small>${(input.files[0].size / 1024).toFixed(2)} KB</small>
                        </div>
                    `);
                }
            }
            
            reader.readAsDataURL(input.files[0]);
        }
    });
}

// Inicialização do formulário
$(document).ready(function() {
    // Configuração do datepicker
    $.datepicker.setDefaults({
        dateFormat: 'dd/mm/yy',
        dayNames: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
        dayNamesMin: ['D', 'S', 'T', 'Q', 'Q', 'S', 'S', 'D'],
        dayNamesShort: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
        monthNamesShort: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        nextText: 'Próximo',
        prevText: 'Anterior',
        showOtherMonths: true,
        changeMonth: true,
        changeYear: true,
        yearRange: '1900:+0'
    });

    // Configuração da submissão do formulário
    $('#contractForm').on('submit', function(e) {
        e.preventDefault();
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        const originalBtnText = $submitBtn.html();
        
        // Desabilita o botão e mostra loading
        $submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...');
        
        // Limpa mensagens de erro anteriores
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').remove();
        
        // Prepara os dados do formulário
        const formData = new FormData($form[0]);
        
        // Envia via AJAX
        $.ajax({
            url: $form.attr('action') || window.location.href,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFTtoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Sucesso
                    showAlert('success', response.message || 'Contrato salvo com sucesso!');
                    
                    // Redireciona após 1,5 segundos
                    setTimeout(() => {
                        window.location.href = response.redirect || '/';
                    }, 1500);
                } else {
                    // Erros de validação
                    if (response.errors) {
                        showValidationErrors($form, response.errors);
                    } else {
                        showAlert('danger', response.message || 'Ocorreu um erro ao processar sua solicitação.');
                    }
                }
            },
            error: function(xhr) {
                let errorMessage = 'Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || errorMessage;
                } catch (e) {
                    console.error('Erro ao processar resposta do servidor:', e);
                }
                showAlert('danger', errorMessage);
            },
            complete: function() {
                $submitBtn.prop('disabled', false).html(originalBtnText);
            }
        });
    });

    // Funções auxiliares
    function showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
            </div>
        `;
        $('#notification-container').html(alertHtml);
    }

    function showValidationErrors($form, errors) {
        // Limpa erros anteriores
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').remove();
        
        // Adiciona classes de erro e mensagens para cada campo com erro
        Object.keys(errors).forEach(fieldName => {
            const $field = $form.find(`[name="${fieldName}"]`);
            const $formGroup = $field.closest('.form-group, .mb-3');
            
            if ($field.length) {
                // Adiciona classe de erro ao campo
                $field.addClass('is-invalid');
                
                // Cria a mensagem de erro
                const errorMessages = Array.isArray(errors[fieldName]) ? 
                    errors[fieldName].join('<br>') : 
                    errors[fieldName];
                
                // Adiciona a mensagem de erro após o campo
                $field.after(`
                    <div class="invalid-feedback">
                        ${errorMessages}
                    </div>
                `);
                
                // Rola até o primeiro campo com erro
                if (Object.keys(errors)[0] === fieldName) {
                    $('html, body').animate({
                        scrollTop: $field.offset().top - 100
                    }, 500);
                }
            } else {
                // Se não encontrar o campo, exibe os erros como uma notificação
                const errorMessages = Array.isArray(errors[fieldName]) ? 
                    errors[fieldName].join('<br>') : 
                    errors[fieldName];
                
                showAlert('danger', `<strong>${fieldName}:</strong> ${errorMessages}`);
            }
        });
        
        // Mostra uma mensagem geral de erro
        showAlert('warning', 'Por favor, corrija os erros no formulário antes de continuar.');
    }
});
