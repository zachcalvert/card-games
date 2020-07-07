import { renderCurrentTurnDisplay } from "./peg.js";

export function renderCurrentCrib(dealer) {
  $('.crib').find('.panel-heading').text(dealer + "'s crib");
}

function buildScoreBoard(players) {

  let colors = ['bg-danger', 'bg-primary', 'bg-success'];

  $.each(players, function(index, player) {
    let points = $('<span/>', {
      id: 'scoreboard-' + player + '-points',
      class: 'player-points',
      html: 0
    });
    let playerName = $('#' + player).find('.player-nickname');
    if (!(playerName.text().includes(': '))) {
      playerName.append(': ');
    }
    playerName.append(points);

    let playerProgressName = $('<span/>', {
      id: player + '-player-progress-name',
      class: 'player-progress-name col-3',
      html: player
    });

    let playerProgressBar = $('<div/>', {
      id: player + '-player-progress-bar',
      class: 'player-progress-bar progress-bar',
      role: 'progressbar',
      style: 'width: 0%'
    });
    let colorClass = colors[index];
    playerProgressBar.addClass(colorClass);

    let playerProgress = $('<div/>', {
      class: 'progress col-9'
     });
    playerProgress.append(playerProgressBar);

    let playerTrack = $('<div/>', {
      id: player + '-player-track',
      class: 'player-track row'
    });

    playerTrack.append(playerProgressName);
    playerTrack.append(playerProgress);
    $('.peg-board').append(playerTrack);
  });
}

export function resetTable() {
  $('.player-card').remove();
  $('.opponent-card').remove();
  $('.crib-card').remove();
  $('.cut-card').remove();
  $('.scoreboard').remove();
  $('.winner').remove();
  $('#play-total').text('');
  $('#deck').show();
  $('.peg-board').children().remove();
  $('.player-points').remove();

  if ($('play-pile')) {
    $('.play-pile').remove();
    $(".player-cards").removeClass(function (index, className) {
      return (className.match(/(^|\s)col-\S+/g) || []).join(' ');
    }).addClass('col-12');
  }
}

export function start(dealer, players) {
  buildScoreBoard(players);
  renderCurrentCrib(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}