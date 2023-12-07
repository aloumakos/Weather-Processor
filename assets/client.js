window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_progress_bar: function(n, col_len ) {
            const style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
            if (col_len !== null && col_len < 16) {
                return [(n*0.1)%30 , style];
            } else {
                return [0 , {"display": "none"}];
            }
        },

        update_countdown: function(n) {
            
            var now = new Date().getTime();
            var report_times = [new Date().setUTCHours(1, 0, 0, 0), new Date().setUTCHours(6, 0, 0, 0), 
                        new Date().setUTCHours(10, 15, 0, 0),
                        new Date().setUTCHours(15, 50, 0, 0)];
            var next_report_time = new Date()
            next_report_time.setUTCDate(next_report_time.getUTCDate() + 1);
            next_report_time.setUTCHours(1, 0, 0, 0);

            for (let time of report_times) {
                if (time > now) {
                    next_report_time = time;
                    
                    switch (report_times.indexOf(time)) {
                        case 0:
                            report = '18';
                            break;
                        case 1:
                            report = '00';
                            break;
                        case 2:
                            report = '06';
                            break;
                        case 3:
                            report = '12';
                            break;
                    }
                    break;
                }   
              }
            const time_difference = next_report_time - now;

            var date = new Date(0);
            date.setMilliseconds(time_difference); 
            var timeString = date.toISOString().substring(11, 19);         
            return `time until next report[${report}]: ${timeString}`
        }
    }
});

