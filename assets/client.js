window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_progress_bar: function(n, col_len ) {
            if (col_len < 16) {
                return (n*0.1)%30 , {"display": "flex"}
            } else {
                return 0 , {"display": "none"}
            }
        }
    }
});