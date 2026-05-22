(function($) {
    $(document).ready(function() {
        const tipoPersonaSelect = $('#id_tipo_persona');
        const divRazonSocial = $('.field-razon_social');
        const divNombres = $('.field-nombres');
        const divApellidos = $('.field-apellidos');
        const inputRazonSocial = $('#id_razon_social');
        const inputNombres = $('#id_nombres');
        const inputApellidos = $('#id_apellidos');

        function toggleFields() {
            const valor = tipoPersonaSelect.val();
            if (valor === 'Juridica') {
                // Ocultar nombres y apellidos
                divNombres.hide();
                divApellidos.hide();
                inputNombres.val('');
                inputApellidos.val('');
                
                // Mostrar razon social
                divRazonSocial.show();
            } else if (valor === 'Natural') {
                // Mostrar nombres y apellidos
                divNombres.show();
                divApellidos.show();
                
                // Ocultar razon social
                divRazonSocial.hide();
                inputRazonSocial.val('');
            } else {
                // Estado por defecto si no hay selección
                divNombres.show();
                divApellidos.show();
                divRazonSocial.show();
            }
        }

        // Ejecutar al iniciar
        toggleFields();

        // Escuchar cambios
        tipoPersonaSelect.on('change', toggleFields);
    });
})(django.jQuery);
