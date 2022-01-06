/* 
Append format
<tr>
    <th scope="row"></th>
    <td>Key issue name</td>
    <td>Percentage</td>
</tr> 

*/

$.ajax({
    url: "/getPercentage",
    dataType: 'json',
    success: function(data){ 
        phillars = Object.keys(data)
        phillars.forEach(function (phillar) {
            keyissues = Object.keys(data[phillar])
            keyissues.forEach(function (item) {
                $("#table-"+phillar).append('<tr> <th scope="row"></th> <td>'+ item +'</td> <td class="percentage">'+ Math.round(data[phillar][item]*100) +'%</td> </tr>');
            });
        });
    }
});