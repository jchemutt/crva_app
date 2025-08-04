$(document).ready(function () {
    $("#searchBox").on("keyup", function () {
        const value = $(this).val().toLowerCase();
        $(".col-md-6.col-lg-4").each(function () {
            const title = $(this).find('.card-header h5').text().toLowerCase();
            $(this).toggle(title.includes(value));
        });
    });
});
