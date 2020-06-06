export function removeCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
  $('#' + player + ' #action-button').text('Play').prop('disabled', true);
}

export function renderCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', '#1CA1F2');
  $('#' + player + ' #action-button').text('Play').prop('disabled', false);
}

export function moveCardFromHandToTable(card, nickname) {
  let handCard = $('#' + card);
  handCard.parent().removeClass('selected');
  handCard.hide();

  let cardImage = $('<img/>', {
    id: card,
    class: 'playedCard',
    src: '/static/img/cards/' + card
  });
  cardImage.attr('belongsto', nickname);
  $('#play-pile').append(cardImage);
}


function animatePlayScore(points) {
  let pointsAlert = $('<span/>', {
    id: 'pointsAlert',
  });
  $("#play-pile").append('+' + pointsAlert);
  $("#pointsAlert").slideUp("slow", function () {
    $("#pointsAlert").remove();
  });
}

export function showCardPlayScore(card, points, nickname, playerPoints) {
  $("#" + nickname).find(".player-points").html(playerPoints);
  console.log(card, points);
  // animatePlayScore(points);
}
