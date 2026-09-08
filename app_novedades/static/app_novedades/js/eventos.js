document.addEventListener("DOMContentLoaded", function() {
    const calendarEl = document.getElementById("calendar");
    const calendar = new FullCalendar.Calendar(calendarEl, {
        noEventsContent: 'No hay eventos disponibles',
        initialView: 'dayGridMonth',
        locale: 'es',
        dayMaxEventRows: true,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,listMonth'
        },
        buttonText: {
            today: 'Hoy',
            month: 'Mes',
            listMonth: 'Agenda',
        },
        events:'/eventos_json',
    });
    calendar.render();
});