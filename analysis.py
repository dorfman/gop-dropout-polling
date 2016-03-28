import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import numpy as np
import pandas as pd
import os
from IPython.display import display, HTML
import stats

def CleanPolls():
    """Get cleaned polling data and further clean it"""
    polls = pd.read_csv('bootPolls.csv')
    
    # Convert date from string to datetime.
    polls.date = pd.Series(pd.DatetimeIndex(polls.date))
    polls.index = polls.date
    del polls['date']
    
    return polls

def GetDropData():
    candidates = pd.read_csv('candidates.csv', index_col='name')
    candidates.date = pd.to_datetime(candidates.date)
    return candidates

def GetBeforeData():
    PollingBeforeDrop = pd.read_csv('PollingBeforeDrop.csv')
    PollingBeforeDrop.index = PollingBeforeDrop['name']
    del PollingBeforeDrop['name']
    PollingBeforeDrop = PollingBeforeDrop.fillna(0)
    return PollingBeforeDrop
    
def GetAfterData():
    PollingAfterDrop = pd.read_csv('PollingAfterDrop.csv')
    PollingAfterDrop.index = PollingAfterDrop['name']
    del PollingAfterDrop['name']
    PollingAfterDrop = PollingAfterDrop.fillna(0)
    return PollingAfterDrop

def GetStats(PollingBeforeDrop, PollingAfterDrop, PollingDiff):
    statFrame = pd.DataFrame(stats.GenStats(PollingBeforeDrop, PollingAfterDrop, PollingDiff))
    statFrame = statFrame[['name', 'Polling Differences', 'Polling of Dropout', 'Polling Sum Negative', 'Polling Sum Positive',
                           'Polling Sum Positive Percentages', 'Polling Sum All Percentages', 'Winner Names', 'Winner Percs', 
                             'Winner Polls Before', 'Winner Polls After', 'Winner Polls Diff']]
    statFrame.index = statFrame.name
    del statFrame['name']
    return statFrame

def SetFontSizes(cands):
    """Sets the labels for the x and y axises. Sets the font sizes for the x and y labels. Set the font size for the
       tick parameters based on how many candidates are still in the race. 
    
    Parameters
    ----------
    cands : list(str)
        The names of the candidates who are still in the race.
    """
    
    font = 8 if len(cands) > 9 else 10
    plt.tick_params(labelsize=font)
    plt.xlabel("Candidates", size=12)
    plt.ylabel("Polling", size=12)
    
def PlotAfter(name, names, PollingAfterDrop):
    """Plots the graph with the polling data after a candidate suspended their campaign.
    
    Parameters
    ----------
    name : str
        The name of the candidate who suspended their campaign.
    names : str
        The names of the candidates who suspended their campaigns. Relevant only to [Paul, Santorum] and [Christie, Fiorina].
    PollingAfterDrop: DataFrame
        Snippet of all polling data a week after a candidate drops out.
    """
    
    actives = PollingAfterDrop.loc[name] != 0
    cands = PollingAfterDrop.columns[actives]
    
    plt.title("Average Polling After " + names + " Suspended Campaign", size=14)
    sns.barplot(cands, PollingAfterDrop.loc[name][actives])
    SetFontSizes(cands)
    
def PlotBefore(name, names, PollingBeforeDrop):
    """Plots the graph with the polling data before a candidate suspended their campaign.
    
    Parameters
    ----------
    name : str
        The name of the candidate who suspended their campaign.
    names : str
        The names of the candidates who suspended their campaigns. Relevant only to [Paul, Santorum] and [Christie, Fiorina].
    PollingBeforeDrop: DataFrame
        Snippet of all polling data a week before a candidate drops out.
    """
    
    actives = PollingBeforeDrop.loc[name] != 0
    cands = PollingBeforeDrop.columns[actives]
    
    plt.title("Average Polling Before " + names + " Suspended Campaign", size=14)
    sns.barplot(cands, PollingBeforeDrop.loc[name][actives])
    SetFontSizes(cands)
    
def DisplayPercentages(ax, percs):
    """Display percentages of the total gained supporters after a candidate drops off.
    
    Parameters
    ----------
    ax : plot
        The Seaborn plot to be displayed.
    percs : Series
        Holds a list of percentages of winnings indexed by candidates.
    """
    
    for p in range(len(ax.patches)):
        height = ax.patches[p].get_height()
        if percs[p] > 0:
            ax.text(ax.patches[p].get_x(), height + 0.25, '%1.1f%%' % (percs[p] * 100), size=18)
            
    if percs[-1] > 0:
        ax.text(ax.patches[-1].get_x(), height + 0.25, '%1.1f%%' % (percs[-1] * 100), size=18)

def PlotDiff(name, names, PollingDiff, statFrame):
    """Plots the graph with the polling difference from before to after a candidate suspended their campaign.
    
    Parameters
    ----------
    name : str
        The name of the candidate who suspended their campaign.
    names : str
        The names of the candidates who suspended their campaigns. Relevant only to [Paul, Santorum] and [Christie, Fiorina].
    PollingDiff: DataFrame
        DataFrame that is the difference between PollingAfterDrop and PollingBeforeDrop
    statFrame: DataFrame
        Holds various stats for polling data
    """
    
    font = 18 if len(names) < 10 else 16
    plt.title("Polling Difference After " + names + " Suspended Campaign", size=font)
    actives = PollingDiff.loc[name] != 0
    if name == 'Santorum':
        actives &= (PollingDiff.loc[name].index != 'Paul')
    if name == 'Christie':
        actives &= (PollingDiff.loc[name].index != 'Fiorina')
    
    cands = PollingDiff.columns[actives]
    data = PollingDiff.loc[name][actives]
    ax = sns.barplot(cands, data)
    plt.tick_params(labelsize=14)
    plt.xlabel("Candidates", size=18)
    plt.ylabel("Polling", size=18)
    plt.ylim(ax.get_ylim()[0] ,data.max() + 1)
    
    percs = statFrame["Polling Sum Positive Percentages"][name]
    del percs[name]
    if name == 'Santorum':
        del percs['Paul'] 
    if name == 'Christie':
        del percs['Fiorina'] 
    
    DisplayPercentages(ax, percs)        
        
def WinningStats(name, statFrame):
    """Prints message analyzing polling data
    
    Parameters
    ----------
    name : str
        The name of the candidate who suspended their campaign.
    statFrame: DataFrame
        Holds various stats for polling data    
    """
    stat = statFrame.loc[name]
    winners = stat['Winner Names']
    
    if len(winners) > 0:
        for w in range(len(winners)):
            print(winners[w] + " gained " + str("%1.2f" % stat['Winner Polls Diff'][w]) + \
                  " percentage points in polling, or " + str("%1.2f" % (stat['Winner Percs'][w] * 100)) + \
                  "% of all polling gains, going up from " + str("%1.2f" % stat['Winner Polls Before'][w]) + \
                  " to " + str("%1.2f" % stat['Winner Polls After'][w]))

        print("after " + name + \
              " suspended his campaign giving up " + str("%1.2f" % (-stat['Polling of Dropout'])) + \
              " polling percentage and other candidates lost a cumulative " + \
              str("%1.2f" % (-stat['Polling Sum Negative'])) + ".")
    else:
        print("No one gained a considerable amount more than anyone else.")

def PlotPolling(name, candidates, statFrame, PollingBeforeDrop, PollingAfterDrop, PollingDiff):
    """Plots the Before, After, and Diff plots.
    
    Parameters
    ----------
    name : str
        The name of the candidate who suspended their campaign.
    candidates: DataFrame
        DataFrame holding candidate dropout data.
    statFrame: DataFrame
        Holds various stats for polling data   
    PollingBeforeDrop: DataFrame
        Snippet of all polling data a week before a candidate drops out.
    PollingAfterDrop: DataFrame
        Snippet of all polling data a week after a candidate drops out.
    PollingDiff: DataFrame
        DataFrame that is the difference between PollingAfterDrop and PollingBeforeDrop
    """
    
    display(HTML("<h4>" + str(candidates['date'][name].date()) + "</h4>"))
    WinningStats(name, statFrame)
    
    names = name
    if names == 'Santorum':
        names = 'Paul and Santorum'
    if names == 'Christie':
        names = 'Christie and Fiorina'
        
    plt.figure(figsize=(20,14))
    plt.subplot2grid((3,4), (0,0), colspan=2)
    PlotBefore(name, names, PollingBeforeDrop)
    plt.subplot2grid((3,4), (0,2), colspan=2)
    PlotAfter(name, names, PollingAfterDrop)
    plt.subplot2grid((3,4), (1,0), colspan=4, rowspan=2)
    PlotDiff(name, names, PollingDiff, statFrame)
    
def GenPollSnippets(polls, candidates):
    """Plots the Before, After, and Diff plots.
    
    Parameters
    ----------
    polls: DataFrame
        All polling data
    candidates: DataFrame
        DataFrame holding candidate dropout data.
    """
    pollList = []
    i = 0
    pollIndex = [c for c in candidates.index if candidates.dropped[c] == True]
    for p in pollIndex:
        pollList.append({'index': i, 'name': p, 'poll': stats.BiWeekPolling(polls, candidates, p)})
        i += 1
    return pollList    
    
    