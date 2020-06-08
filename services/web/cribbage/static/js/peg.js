export function removeCurrentTurnDisplay(player) {
  $("#" + player).find(".panel-heading").css('background', 'rgb(21, 32, 43)');
  $('#' + player + ' #action-button').text('Play').prop('disabled', true);
}

export function renderCurrentTurnDisplay(player, action) {
  $("#" + player).find(".panel-heading").css('background', '#1CA1F2');
  $('#' + player + ' #action-button').text(action).prop('disabled', false);
}

function moveCardFromHandToTable(card, nickname) {
  let handCard = $('#' + card);
  handCard.parent().removeClass('selected');
  handCard.hide();

  let cardImage = $('<img/>', {
    class: 'playedCard',
    src: '/static/img/cards/' + card
  });
  $('#play-pile').append(cardImage);
}


function updateRunningTotal(new_total) {
  let current = $("#play-total").text();

  $({someValue: current}).animate({someValue: new_total}, {
      duration: 500,
      easing:'swing', // can be anything
      step: function() { // called on every step
          // Update the element's text with rounded-up value:
          $('#play-total').text(Math.round(this.someValue));
      }
  });
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

function updatePlayerScore(nickname, points_scored) {
  console.log('updating ' + nickname + 's score to ' + points_scored);
  let playerPoints = $("#" + nickname).find(".player-points");
  let current = parseInt(playerPoints.text());
  console.log(nickname + ' currently has ' + current + ' points');

  $({someValue: current}).animate({someValue: current + points_scored}, {
      duration: 500,
      easing:'swing', // can be anything
      step: function() { // called on every step
          // Update the element's text with rounded-up value:
          $(playerPoints).text(Math.round(this.someValue));
      }
  });
}

export function scorePlay(msg) {
  moveCardFromHandToTable(msg.card, msg.nickname);
  if (msg.points_scored > 0) {
    animatePlayScore(msg.card, msg.points_scored);
    updatePlayerScore(msg.nickname, msg.points_scored);
  }
  updateRunningTotal(msg.new_total);
  removeCurrentTurnDisplay(msg.nickname);
  renderCurrentTurnDisplay(msg.next_player, msg.next_player_action);
}