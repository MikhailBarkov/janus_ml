def model_to_dict(model) -> dict:
    model_params = {
        'name': model.NAME,
        'layers': [],
    }

    for i, layer in enumerate(model.layers):
        layer_params = {
            'name': ''
        }

        for label, tansor in layer.state_dict():


        model_params['layers'].append()