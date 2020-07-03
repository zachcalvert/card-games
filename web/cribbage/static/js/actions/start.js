import { renderCurrentTurnDisplay } from "./peg.js";

export function renderCurrentCrib(dealer) {
  $('.crib').find('.panel-heading').text(dealer + "'s crib");
}

function buildScoreBoard(players) {
  $.each(players, function(index, player) {
    let points = $('<span/>', {
      id: 'scoreboard-' + player + '-points',
      html: 0
    });
    let playerName = $('#' + player).find('.player-nickname');
    playerName.append(': ');
    playerName.append(points);

    let playerTrackName = $('<span/>', {
      id: player + '-player-track-name',
      class: 'player-track-name col-3',
      html: player
    });

    let playerTrackBar = $('<progress/>', {
      id: player + '-player-track-bar',
      class: 'player-track-bar col-9',
      max: 121,
      value: 0
    });

    let playerTrack = $('<div/>', {
      id: player + '-player-track',
      class: 'player-track row'
    });

    playerTrack.append(playerTrackName);
    playerTrack.append(playerTrackBar);
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
}

export function start(dealer, players) {
  buildScoreBoard(players);
  renderCurrentCrib(dealer);
  renderCurrentTurnDisplay(dealer, 'DEAL');
}