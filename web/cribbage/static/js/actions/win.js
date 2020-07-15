export function decorateWinner(winner) {
  let playerName = $('#' + winner).find('.player-nickname');
  playerName.append('<span class="winner fas fa-crown"></span>');
}

export function drawGameSummary(gameName) {
  $.ajax({
    type: 'POST',
    url: "/game_summary/",
    data: {'game': gameName}
  }).done(function (response) {
    console.log(response);
    $('.opponent').hide();

    let gameSummary = $('<div/>', {
      class: 'game-summary'
    });

    let table = $('<table>').addClass('table table-dark table-striped table-responsive');
    let thead = $('<thead>');
    thead.append('<tr>');
    let tbody = $('<tbody>');

    let nameCell = $('<td/>', {
      id: 'summary-header-name',
      html: 'player'
    });
    thead.find('tr').append(nameCell);

    let playCell = $('<td/>', {
      id: 'summary-header-play',
      html: 'from play'
    });
    thead.find('tr').append(playCell);

    let handCell = $('<td/>', {
      id: 'summary-header-hand',
      html: 'from hand'
    });
    thead.find('tr').append(handCell);

    let cribCell = $('<td/>', {
      id: 'summary-header-crib',
      html: 'from crib'
    });
    thead.find('tr').append(cribCell);

    let totalCell = $('<td/>', {
      id: 'summary-header-total',
      html: 'total'
    });
    thead.find('tr').append(totalCell);

    $.each(response, function (player, dict) {
      let playerRow = $('<tr/>');
      let nameCell = $('<td/>', {
        id: 'summary-player-name',
        html: player
      });
      playerRow.append(nameCell);
      $.each(dict, function (key, value) {
        let pointsCell = $('<td/>', {
          id: 'summary-player-' + key,
          html: value
        });
        playerRow.append(pointsCell);
      });
      tbody.append(playerRow);
    });

    table.append(thead);
    table.append(tbody);
    gameSummary.append(table);
    $('.opponents').append(gameSummary);
    console.log('here');
  });
};