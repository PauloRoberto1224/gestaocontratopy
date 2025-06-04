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
    // Remove todos os caracteres não numéricos e limita a 7 dígitos
    let value = input.val().replace(/[^\d]/g, '').substring(0, 7);
    
    // Atualiza o valor formatado (apenas números, sem formatação)
    input.val(value);
    
    // Retorna o valor sem formatação para validação
    return value;
}

function formatCNPJ(input) {
    // Remove todos os caracteres não numéricos
    let value = input.val().replace(/[^\d]/g, '');
    
    // Formata CNPJ: 00.000.000/0000-00
    if (value.length > 0) {
        value = value.replace(/^(\d{2})(\d)/, "$1.$2");
        value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
        value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
        value = value.replace(/(\d{4})(\d)/, "$1-$2");
    }
    
    // Atualiza o valor formatado
    input.val(value);
    
    // Retorna o valor sem formatação para validação
    return value.replace(/[^\d]/g, '');
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

    /**
     * Configuração da submissão do formulário
     * Esta função lida com o envio do formulário via AJAX, mostrando feedback apropriado ao usuário
     * e tratando diferentes tipos de respostas do servidor.
     */
    $('#contractForm').on('submit', function(e) {
        e.preventDefault();
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        const originalBtnText = $submitBtn.html();
        
        // Desabilita o botão e mostra loading
        $submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> ' +
            '<span class="submit-text">Salvando...</span>'
        );
        
        // Limpa mensagens de erro e estados anteriores
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback, .alert-dismissible').remove();
        
        // Prepara os dados do formulário
        const formData = new FormData($form[0]);
        
        // Configuração global do AJAX
        $.ajaxSetup({
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val() || ''
            },
            cache: false,
            processData: false,
            contentType: false
        });
        
        // Variável para controlar se já foi mostrado um erro
        let errorShown = false;
        
        // Envia via AJAX
        $.ajax({
            url: $form.attr('action') || window.location.href,
            type: 'POST',
            data: formData,
            dataType: 'json',
            timeout: 30000, // 30 segundos de timeout
            
            /**
             * Manipulador de sucesso da requisição AJAX
             * @param {Object} response - Resposta do servidor
             */
            success: function(response) {
                // Verifica se a resposta é um objeto válido
                if (typeof response !== 'object' || response === null) {
                    console.error('Resposta do servidor em formato inesperado:', response);
                    showAlert({
                        type: 'danger',
                        title: 'Erro no processamento',
                        message: 'Resposta inesperada do servidor. Por favor, tente novamente.',
                        icon: 'exclamation-triangle',
                        timeout: 10000
                    });
                    return;
                }

                // Sucesso na operação
                if (response.success || response.status === 'success') {
                    const successMessage = response.message || 'Operação realizada com sucesso!';
                    const redirectUrl = response.redirect || window.location.href;
                    const delay = response.delay || 2000;
                    
                    // Exibe mensagem de sucesso
                    showAlert({
                        type: 'success',
                        message: successMessage,
                        icon: 'check-circle',
                        timeout: 5000,
                        position: 'top-center'
                    });
                    
                    // Se houver um redirecionamento, desabilita o formulário
                    if (redirectUrl) {
                        // Adiciona classe de sucesso ao formulário
                        $form.addClass('was-validated');
                        
                        // Desabilita todos os campos
                        $form.find('input, textarea, select, button')
                            .prop('disabled', true)
                            .addClass('disabled');
                        
                        // Redireciona após o tempo definido
                        const redirectTimer = setTimeout(() => {
                            // Verifica se é um redirecionamento para a mesma página (atualização)
                            if (redirectUrl === window.location.pathname || 
                                redirectUrl === window.location.href) {
                                window.location.reload();
                            } else {
                                window.location.href = redirectUrl;
                            }
                        }, delay);
                        
                        // Armazena o timer no formulário para possível cancelamento
                        $form.data('redirectTimer', redirectTimer);
                    }
                } 
                // Erros de validação ou outros erros não críticos
                else {
                    // Se houver erros de validação específicos
                    if (response.errors) {
                        const hasFieldErrors = showValidationErrors($form, response.errors, {
                            scrollToFirstError: true,
                            focusFirstError: true
                        });
                        
                        // Mostra mensagem de erro geral apenas se não houver erros de campo específicos
                        if (!hasFieldErrors || Object.keys(response.errors).length === 0) {
                            showFormError($form, response.message || 'Por favor, verifique os dados informados.', {
                                title: 'Erro de validação',
                                icon: 'exclamation-triangle'
                            });
                        } else {
                            // Rola até o topo do formulário para mostrar a mensagem de erro
                            $('html, body').animate({
                                scrollTop: $form.offset().top - 20
                            }, 500);
                        }
                    } 
                    // Se houver apenas uma mensagem de erro
                    else if (response.message) {
                        showFormError($form, response.message, {
                            title: 'Atenção',
                            icon: 'info-circle'
                        });
                    } 
                    // Erro genérico
                    else {
                        showAlert({
                            type: 'danger',
                            title: 'Erro',
                            message: 'Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente.',
                            icon: 'exclamation-triangle',
                            timeout: 10000
                        });
                    }
                }
            },
            
            /**
             * Manipulador de erros da requisição AJAX
             * @param {Object} xhr - Objeto XMLHttpRequest
             * @param {string} status - Status do erro
             * @param {string} error - Mensagem de erro
             */
            error: function(xhr, status, error) {
                // Evita mostrar múltiplos erros
                if (errorShown) return;
                errorShown = true;
                
                // Tenta obter a resposta JSON, se disponível
                let response = {};
                try {
                    response = xhr.responseJSON || {};
                } catch (e) {
                    console.error('Erro ao analisar resposta JSON:', e);
                }
                
                // Mensagem de erro padrão
                const defaultMessage = 'Ocorreu um erro inesperado. Por favor, tente novamente.';
                
                // Trata diferentes códigos de status HTTP
                switch (xhr.status) {
                    // Erro de validação (400 Bad Request)
                    case 400:
                        if (response.errors) {
                            const hasFieldErrors = showValidationErrors($form, response.errors, {
                                scrollToFirstError: true,
                                focusFirstError: true
                            });
                            
                            if (!hasFieldErrors || Object.keys(response.errors).length === 0) {
                                showFormError($form, response.message || 'Por favor, verifique os dados informados.', {
                                    title: 'Erro de validação',
                                    icon: 'exclamation-triangle'
                                });
                            }
                        } else {
                            showFormError($form, response.message || 'Erro ao processar o formulário. Verifique os campos e tente novamente.', {
                                title: 'Erro de validação',
                                icon: 'exclamation-triangle'
                            });
                        }
                        break;
                        
                    // Erro de autenticação (401 Unauthorized)
                    case 401:
                        showAlert({
                            type: 'warning',
                            title: 'Sessão expirada',
                            message: 'Sua sessão expirou. Por favor, faça login novamente.',
                            icon: 'sign-in-alt',
                            timeout: 5000,
                            onClose: () => {
                                window.location.href = '/accounts/login/?next=' + 
                                    encodeURIComponent(window.location.pathname + window.location.search);
                            }
                        });
                        break;
                        
                    // Acesso negado (403 Forbidden)
                    case 403:
                        showAlert({
                            type: 'danger',
                            title: 'Acesso negado',
                            message: response.message || 'Você não tem permissão para realizar esta ação.',
                            icon: 'ban',
                            timeout: 10000
                        });
                        break;
                        
                    // Recurso não encontrado (404 Not Found)
                    case 404:
                        showAlert({
                            type: 'warning',
                            title: 'Recurso não encontrado',
                            message: response.message || 'O recurso solicitado não foi encontrado.',
                            icon: 'search',
                            timeout: 10000,
                            onClose: () => {
                                // Recarrega a página após 3 segundos
                                setTimeout(() => window.location.reload(), 3000);
                            }
                        });
                        break;
                        
                    // Erro do servidor (500 Internal Server Error)
                    case 500:
                        showAlert({
                            type: 'danger',
                            title: 'Erro no servidor',
                            message: response.message || 'Ocorreu um erro no servidor. Por favor, tente novamente mais tarde.',
                            icon: 'server',
                            timeout: 15000
                        });
                        break;
                        
                    // Sem conexão com o servidor
                    case 0:
                        showAlert({
                            type: 'danger',
                            title: 'Sem conexão',
                            message: 'Não foi possível conectar ao servidor. Verifique sua conexão com a internet e tente novamente.',
                            icon: 'wifi',
                            timeout: 0,
                            dismissible: false
                        });
                        break;
                        
                    // Timeout da requisição
                    case 'timeout':
                        showAlert({
                            type: 'warning',
                            title: 'Tempo esgotado',
                            message: 'A requisição demorou muito para ser processada. Verifique sua conexão e tente novamente.',
                            icon: 'clock',
                            timeout: 10000
                        });
                        break;
                        
                    // Outros erros
                    default:
                        showAlert({
                            type: 'danger',
                            title: 'Erro ' + (xhr.status || 'desconhecido'),
                            message: response.message || defaultMessage,
                            icon: 'exclamation-circle',
                            timeout: 10000
                        });
                }
            },
            
            /**
             * Manipulador de conclusão da requisição AJAX
             * Executado sempre, independentemente de sucesso ou falha
             */
            complete: function() {
                // Reativa o botão de envio
                $submitBtn.prop('disabled', false).html(originalBtnText);
                
                // Executa callback onComplete se fornecido
                if (typeof config.onComplete === 'function') {
                    try {
                        config.onComplete($form);
                    } catch (e) {
                        console.error('Erro no callback onComplete:', e);
                    }
                }
            }
        });
    });

    /**
     * Exibe uma mensagem de erro no topo do formulário
     * @param {jQuery} $form - Elemento jQuery do formulário
     * @param {string|Array|Object} message - Mensagem de erro a ser exibida (pode ser string, array de strings ou objeto com detalhes)
     * @param {Object} [options={}] - Opções de configuração
     * @param {string} [options.title='Erro ao processar o formulário'] - Título da mensagem de erro
     * @param {string} [options.icon='exclamation-triangle'] - Ícone a ser exibido (classe Font Awesome sem o prefixo)
     * @param {number} [options.timeout=0] - Tempo em ms para fechar automaticamente (0 = não fecha)
     * @param {boolean} [options.scrollToTop=true] - Se deve rolar até o topo do formulário
     * @param {boolean} [options.focusFirstField=true] - Se deve focar no primeiro campo do formulário
     * @param {string} [options.position='top'] - Posição da mensagem ('top' ou 'before' para antes do formulário, 'prepend' para dentro do formulário)
     * @param {Function} [options.onClose] - Função chamada quando o alerta é fechado
     * @param {string} [options.id='form-errors'] - ID do elemento de erro
     * @returns {jQuery} O elemento jQuery do alerta criado
     */
    function showFormError($form, message, options = {}) {
        // Validação dos parâmetros
        if (!$form || !$form.length) {
            console.error('Formulário inválido para exibição de erro');
            return $();
        }
        
        // Configurações padrão
        const config = {
            title: 'Erro ao processar o formulário',
            icon: 'exclamation-triangle',
            timeout: 0, // Não fecha automaticamente por padrão
            scrollToTop: true,
            focusFirstField: true,
            position: 'top', // 'top' (antes do formulário) ou 'prepend' (dentro do formulário)
            id: 'form-errors',
            onClose: null,
            ...options
        };
        
        // Remove mensagens de erro anteriores com o mesmo ID
        $(`#${config.id}`).remove();
        
        // Processa a mensagem (pode ser string, array ou objeto)
        let messageHtml = '';
        if (typeof message === 'string') {
            messageHtml = `<p class="mb-0 mt-1">${message}</p>`;
        } else if (Array.isArray(message)) {
            messageHtml = '<ul class="mb-0 mt-2 ps-3">' + 
                message.map(msg => `<li>${msg}</li>`).join('') + 
                '</ul>';
        } else if (typeof message === 'object' && message !== null) {
            // Se for um objeto, assume que é um objeto de erros do Django
            const errorList = [];
            for (const [field, errors] of Object.entries(message)) {
                const fieldLabel = $form.find(`label[for="${field}"]`).text() || 
                                 field.replace(/_/g, ' ').replace(/\w\S*/g, txt => 
                                     txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
                                 );
                errorList.push(`<li><strong>${fieldLabel}:</strong> ${Array.isArray(errors) ? errors.join(', ') : errors}</li>`);
            }
            messageHtml = '<div class="alert-errors"><ul class="mb-0 mt-2 ps-3">' + 
                        errorList.join('') + 
                        '</ul></div>';
        }
        
        // Cria o HTML do alerta de erro
        const iconHtml = config.icon ? `<i class="fas fa-${config.icon} me-2"></i>` : '';
        const alertId = config.id;
        const alertHtml = `
            <div id="${alertId}" class="alert alert-danger alert-dismissible fade show" role="alert">
                <div class="d-flex align-items-center">
                    <div class="flex-shrink-0">
                        ${iconHtml}
                    </div>
                    <div class="flex-grow-1 ms-2">
                        <h5 class="alert-heading mb-1">${config.title}</h5>
                        ${messageHtml || '<p class="mb-0">Por favor, verifique os dados informados e tente novamente.</p>'}
                    </div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
                </div>
            </div>
        `;
        
        // Adiciona o alerta ao DOM conforme a posição especificada
        let $alert;
        if (config.position === 'prepend') {
            $alert = $(alertHtml).prependTo($form);
        } else {
            // Por padrão, adiciona antes do formulário
            $alert = $(alertHtml).insertBefore($form);
        }
        
        // Inicializa o componente de alerta do Bootstrap
        if ($alert.length) {
            // Adiciona evento para quando o alerta for totalmente exibido
            $alert.on('shown.bs.alert', function() {
                // Rola até o topo do formulário se configurado
                if (config.scrollToTop) {
                    $('html, body').stop().animate({
                        scrollTop: $form.offset().top - 20
                    }, 500);
                }
                
                // Foca no primeiro campo do formulário se configurado
                if (config.focusFirstField) {
                    const $firstField = $form.find('input:not([type=hidden]):not([disabled]), ' +
                                                 'select:not([disabled]), ' +
                                                 'textarea:not([disabled])').first();
                    if ($firstField.length) {
                        try {
                            // Para campos Select2, foca no elemento de busca
                            if ($firstField.hasClass('select2-hidden-accessible')) {
                                $firstField.select2('open');
                            } else {
                                $firstField.trigger('focus');
                            }
                        } catch (e) {
                            console.warn('Não foi possível focar no campo:', e);
                        }
                    }
                }
            });
            
            // Adiciona evento para quando o alerta for fechado
            $alert.on('closed.bs.alert', function() {
                // Executa o callback onClose se fornecido
                if (typeof config.onClose === 'function') {
                    try {
                        config.onClose($form);
                    } catch (e) {
                        console.error('Erro no callback onClose:', e);
                    }
                }
                
                // Remove o elemento do DOM após a animação
                $(this).remove();
            });
            
            // Configura o timeout para fechar automaticamente se especificado
            if (config.timeout > 0) {
                setTimeout(() => {
                    $alert.alert('close');
                }, config.timeout);
            }
        }
        
        return $alert;
    }
    
    /**
     * Exibe uma mensagem de alerta para o usuário
     * @param {string} type - Tipo de alerta (success, danger, warning, info, primary, secondary)
     * @param {string|object} message - Mensagem a ser exibida ou objeto com opções
     * @param {object} [options] - Opções adicionais (opcional)
     * @param {number} [options.timeout=5000] - Tempo em ms para o alerta desaparecer (0 = não fecha)
     * @param {boolean} [options.append=false] - Se true, adiciona ao invés de substituir
     * @param {string} [options.title] - Título opcional para o alerta
     * @param {string} [options.icon] - Ícone opcional (classe Font Awesome sem o prefixo)
     * @param {string} [options.position='top-right'] - Posição do alerta (top-right, top-left, bottom-right, bottom-left, top-center, bottom-center)
     * @param {boolean} [options.dismissible=true] - Se o alerta pode ser fechado
     * @param {function} [options.onClose] - Função chamada quando o alerta é fechado
     * @param {function} [options.onShow] - Função chamada quando o alerta é exibido
     * @param {string} [options.container='#notification-container'] - Seletor do container do alerta
     * @param {string} [options.animation='fade'] - Animação (fade, slide, none)
     * @returns {jQuery} O elemento jQuery do alerta criado
     */
    function showAlert(type, message, options = {}) {
        // Se a mensagem for um objeto, extrai as opções
        if (typeof message === 'object' && message !== null) {
            options = { ...message, ...options };
            message = options.message || '';
            type = options.type || type || 'info';
        }
        
        // Validação dos parâmetros
        if (typeof message === 'undefined') {
            console.error('Mensagem não fornecida para o alerta');
            return $();
        }
        
        // Configurações padrão
        const config = {
            timeout: 5000,
            append: false,
            title: '',
            icon: '',
            position: 'top-right',
            dismissible: true,
            container: '#notification-container',
            animation: 'fade',
            onClose: null,
            onShow: null,
            ...options
        };
        
        // Mapeia tipos para ícones e cores padrão
        const iconMap = {
            success: { icon: 'check-circle', color: 'success' },
            danger: { icon: 'exclamation-triangle', color: 'danger' },
            warning: { icon: 'exclamation-triangle', color: 'warning' },
            info: { icon: 'info-circle', color: 'info' },
            primary: { icon: 'info-circle', color: 'primary' },
            secondary: { icon: 'info-circle', color: 'secondary' }
        };
        
        // Obtém as configurações do tipo de alerta
        const alertType = iconMap[type] || iconMap.info;
        
        // Define o ícone se não foi especificado
        const iconClass = config.icon || alertType.icon;
        const iconHtml = iconClass ? `<i class="fas fa-${iconClass} me-2"></i>` : '';
        
        // Cria um ID único para o alerta
        const alertId = `alert-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
        
        // Cria as classes CSS baseadas nas opções
        const alertClasses = [
            'alert',
            `alert-${alertType.color}`,
            'alert-dismissible',
            'fade',
            'show',
            `alert-${config.position}`,
            `alert-${config.animation}`
        ];
        
        // Cria o HTML do alerta
        const titleHtml = config.title ? `<strong class="alert-title">${config.title}</strong><br>` : '';
        const closeButton = config.dismissible ? 
            '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>' : '';
        
        const alertHtml = `
            <div id="${alertId}" class="${alertClasses.join(' ')}" role="alert">
                <div class="alert-content">
                    ${iconHtml}
                    <div class="alert-message">
                        ${titleHtml}
                        <span class="alert-text">${message}</span>
                    </div>
                    ${closeButton}
                </div>
            </div>
        `;
        
        // Encontra ou cria o container de notificações
        let $container = $(config.container);
        if (!$container.length) {
            // Cria o container se não existir
            $container = $('<div>', { 
                id: 'notification-container',
                class: 'notifications-container'
            }).appendTo('body');
        }
        
        // Adiciona classes de posição ao container
        $container.addClass(`notifications-${config.position.replace('-', '-')}`);
        
        // Adiciona o alerta ao DOM
        if (config.append) {
            $container.append(alertHtml);
        } else {
            $container.prepend(alertHtml);
        }
        
        const $alert = $(`#${alertId}`);
        
        // Configura o timeout para fechar automaticamente
        let timeoutId;
        if (config.timeout > 0) {
            timeoutId = setTimeout(() => {
                if ($alert.length) {
                    $alert.alert('close');
                }
            }, config.timeout);
        }
        
        // Inicializa o componente de alerta do Bootstrap
        if ($alert.length) {
            // Dispara o evento onShow se fornecido
            if (typeof config.onShow === 'function') {
                try {
                    config.onShow($alert);
                } catch (e) {
                    console.error('Erro no callback onShow:', e);
                }
            }
            
            // Adiciona evento para quando o alerta for fechado
            $alert.on('closed.bs.alert', function () {
                // Limpa o timeout se o alerta for fechado manualmente
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
                
                // Executa o callback onClose se fornecido
                if (typeof config.onClose === 'function') {
                    try {
                        config.onClose();
                    } catch (e) {
                        console.error('Erro no callback onClose:', e);
                    }
                }
                
                // Remove o elemento do DOM após a animação
                $(this).remove();
            });
        }
        
        return $alert;
    }
    
    /**
     * Exibe erros de validação nos campos do formulário
     * @param {jQuery} $form - Elemento jQuery do formulário
     * @param {Object} errors - Objeto contendo os erros de validação
     * @param {Object} options - Opções adicionais (opcional)
     * @param {boolean} [options.scrollToFirstError=true] - Se deve rolar até o primeiro erro
     * @param {boolean} [options.focusFirstError=true] - Se deve focar no primeiro campo com erro
     * @param {string} [options.errorClass='is-invalid'] - Classe CSS para campos com erro
     * @param {string} [options.feedbackClass='invalid-feedback'] - Classe CSS para mensagens de erro
     */
    function showValidationErrors($form, errors, options = {}) {
        // Configurações padrão
        const config = {
            scrollToFirstError: true,
            focusFirstError: true,
            errorClass: 'is-invalid',
            feedbackClass: 'invalid-feedback',
            ...options
        };

        // Validação dos parâmetros
        if (!$form || !$form.length) {
            console.error('Formulário inválido:', $form);
            return false;
        }

        if (!errors || typeof errors !== 'object' || Object.keys(errors).length === 0) {
            console.warn('Nenhum erro de validação fornecido:', errors);
            return false;
        }

        let hasFieldErrors = false;
        let firstErrorField = null;
        const errorFields = [];
        const processedFields = new Set();

        // Itera sobre cada campo com erro
        $.each(errors, function(field, errorList) {
            if (!Array.isArray(errorList) || errorList.length === 0) {
                return; // Pula iterações inválidas
            }

            const fieldName = field.replace(/\[\d+\]/g, ''); // Remove índices de arrays
            let $field = $form.find(`[name$="${fieldName}"], [name="${field}"]`).first();
            
            // Se não encontrou pelo name, tenta encontrar por data-name ou id
            if (!$field.length) {
                $field = $form.find(`[data-name="${field}"], #${field}`).first();
                if (!$field.length) {
                    console.warn(`Campo não encontrado: ${field}`);
                    return; // Pula campos não encontrados
                }
            }

            // Evita processar o mesmo campo várias vezes
            const fieldId = $field.attr('id') || $field.attr('name');
            if (processedFields.has(fieldId)) {
                return;
            }
            processedFields.add(fieldId);

            // Encontra o grupo de formulário mais próximo
            const $formGroup = $field.closest('.form-group, .mb-3, .form-floating, .input-group, .form-control, .form-select').length ? 
                             $field.closest('.form-group, .mb-3, .form-floating, .input-group, .form-control, .form-select') : 
                             $field.parent();
            
            // Adiciona a classe de erro ao campo
            $field.addClass(config.errorClass);
            
            // Processa as mensagens de erro
            const errorMessages = errorList.map(error => {
                return typeof error === 'object' && error.message ? error.message : String(error);
            }).join('<br>');
            
            // Remove mensagens de erro anteriores para este campo
            $formGroup.find(`.${config.feedbackClass}`).remove();
            
            // Cria o elemento de feedback
            const $feedback = $(`<div class="${config.feedbackClass} d-block">${errorMessages}</div>`);
            
            // Posiciona o feedback de acordo com o tipo de campo
            if ($field.is(':checkbox, :radio') && $field.closest('.form-check').length) {
                // Para checkboxes e radios dentro de form-check
                $field.closest('.form-check').after($feedback);
            } 
            else if ($field.closest('.input-group').length) {
                // Para campos com input-group
                $field.closest('.input-group').after($feedback);
            }
            else if ($field.is('select') && $field.next('.select2-container').length) {
                // Para campos Select2
                $field.next('.select2-container').after($feedback);
            }
            else {
                // Para campos normais
                $field.after($feedback);
            }
            
            // Marca que encontrou pelo menos um campo com erro
            hasFieldErrors = true;
            
            // Armazena o primeiro campo com erro para rolagem
            if (!firstErrorField) {
                firstErrorField = $field;
                errorFields.push($field);
            }
        });
        
        // Rola até o primeiro campo com erro, se necessário
        if (config.scrollToFirstError && firstErrorField && firstErrorField.length) {
            const offset = firstErrorField.offset();
            if (offset) {
                const navbarHeight = $('.navbar').outerHeight() || 0;
                const scrollPosition = Math.max(0, offset.top - navbarHeight - 20);
                
                $('html, body').stop().animate({
                    scrollTop: scrollPosition
                }, 500, 'swing', function() {
                    // Foca no primeiro campo com erro após a animação de rolagem
                    if (config.focusFirstError) {
                        try {
                            // Para campos Select2, foca no elemento de busca
                            if (firstErrorField.hasClass('select2-hidden-accessible')) {
                                firstErrorField.select2('open');
                            } else {
                                firstErrorField.trigger('focus');
                            }
                        } catch (e) {
                            console.warn('Não foi possível focar no campo:', firstErrorField, e);
                        }
                    }
                });
            }
        }
        
        // Se não encontrou nenhum campo específico, mostra uma mensagem geral
        if (!hasFieldErrors) {
            const errorMessage = 'Ocorreu um erro ao processar o formulário. ';
            const suggestion = Object.keys(errors).length > 0 ? 
                'Por favor, verifique os dados fornecidos.' : 
                'Tente novamente mais tarde.';
                
            showAlert({
                type: 'danger',
                title: 'Erro de validação',
                message: errorMessage + suggestion,
                icon: 'exclamation-triangle',
                timeout: 10000
            });
            
            console.warn('Erros de validação não mapeados para campos do formulário:', errors);
        }
        
        return hasFieldErrors;
    }
});
