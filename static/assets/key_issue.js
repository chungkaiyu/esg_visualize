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
            if ( phillar=="selected_company" ){
                if ( data['selected_company'].includes("Applied") ){
                    $("#title").html("Applied's Key Issue Level of Relevance");
                    $(".subtitle").html("Level of<br>Relevance");
                } 
                else{
                    $("#title").html("Key Issue Level of Relevance－"+data['selected_company'].split('-')[1]+" / Applied");
                    $(".subtitle").html(data['selected_company'].split('-')[1]+"/Applied");
                }    
            }
            else{
                for ( var i=0; i<data[phillar]['k_name'].length; i++ ){
                    if ( data['selected_company'].includes("Applied") ){
                        $("#table-"+phillar).append('<tr><td colspan="2">'+ data[phillar]['k_name'][i] +
                            '</td> <td class="percentage" colspan="2">'+ (data[phillar]['s_weight'][i]*100).toFixed(2)+
                            '%</td></tr>');
                    }
                    else{
                        $("#table-"+phillar).append('<tr><td colspan="2">'+ data[phillar]['k_name'][i] +
                            '</td> <td class="percentage" colspan="1">'+ (data[phillar]['s_weight'][i]*100).toFixed(2) +
                            '%</td> <td class="percentage" colspan="1">' + (data[phillar]['a_weight'][i]*100).toFixed(2) +'%</td> </tr>');
                    }
                }
            }
            
            // keyissues = Object.keys(data[phillar])
            // keyissues.forEach(function (item) {
            //     $("#table-"+phillar).append('<tr> <th scope="row"></th> <td>'+ item +'</td> <td class="percentage">'+ Math.round(data[phillar][item]*100) +'%</td> </tr>');
            // });
        });
    }
});

$(function () {
    $("[data-toggle='tooltip']").tooltip();
});