window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_progress_bar: function(n, col_len ) {
            const style = {'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
            if (col_len < 16) {
                return (n*0.1)%30 , style
            } else {
                return 0 , {"display": "none"}
            }
        }
    }
});