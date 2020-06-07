export function removeCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
  $('#' + player + ' #action-button').text('Play').prop('disabled', true);
}

export function renderCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', '#1CA1F2');
  $('#' + player + ' #action-button').text('Play').prop('disabled', false);

}

function moveCardFromHandToTable(card, nickname) {
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

  let done_playing = true;
  $('#' + nickname + ' img').each(function(){
    if ($(this).is(':visible')) {
      console.log($(this) + ' is visible');
      done_playing = false;
    }
  });
  if (done_playing) {
    $("#action-button").text('Pass');
  }

}


function updateRunningTotal(new_total) {
  $("#play-total").html(new_total);
}

function animatePlayScore(card, points) {
  console.log('playing card ' + card + ' earned ' + points + ' points');
  if (points > 0) {
    let pointsAlert = $('<div/>', {
      id: 'pointsAlert',
      html: '+' + points
    });
    $("#play-pile").append(pointsAlert);
    $("#pointsAlert").animate({"top": "-=50px"}, 500,"linear",function() {
      $(this).remove();
    });
  }
}

function updatePlayerScore(nickname, new_total) {
  let playerPoints = $("#" + nickname).find(".player-points");
  playerPoints.animate({ fontSize: "24px" }, 500);
  playerPoints.html(new_total);
  playerPoints.animate({ fontSize: "16px" }, 500);
}

export function scorePlay(msg) {
  moveCardFromHandToTable(msg.card, msg.nickname);
  if (msg.points > 0) {
    animatePlayScore(msg.card, msg.points);
    updatePlayerScore(msg.nickname, msg.player_points);
  }
  updateRunningTotal(msg.new_total);
}