"""
Google Sheets Dashboard Builder Module.
Constructs executive KPI cards, summary aggregation tables, native Google Charts,
and dark navy/white professional styling on the Dashboard worksheet.
"""

import logging
from typing import Dict, Any, List
from googleapiclient.discovery import Resource

from core.sheets_sync_engine import execute_with_backoff

logger = logging.getLogger(__name__)


def build_executive_dashboard(
    service: Resource,
    spreadsheet_id: str,
    dashboard_sheet_id: int
) -> Dict[str, Any]:
    """
    Builds the executive dashboard on the Dashboard worksheet:
    1. Title banner and metadata
    2. Executive KPI summary cards
    3. Category and trend summary tables
    4. Native Google Sheets charts
    """
    # 1. Populate Dashboard values (Title, KPI Cards, and Aggregation Formulas)
    values_data = [
        # Row 1: Title
        ["AI ECOSYSTEM INTELLIGENCE DASHBOARD", "", "", "", "", "", "", "", "", "", "", ""],
        # Row 2: Subtitle & Timestamp
        ["Six-Month Rolling Intelligence Pipeline — Phase IV Live Synchronization", "", "", "", "", "", "", "", "", "", "", ""],
        # Row 3: Blank
        ["", "", "", "", "", "", "", "", "", "", "", ""],
        # Row 4: KPI Card Headers (Content KPIs strictly separated from Repository & Operational Telemetry)
        [
            "Total Startups", "Total Products", "Total Research Papers",
            "Total AI News", "Total AI Jobs", "Six-Month Eligible Content",
            "Fresh Content (24 Hours)", "Tracked GitHub Repositories", "GitHub Metric Snapshots",
            "Pipeline Collection Runs"
        ],
        # Row 5: KPI Card Formulas
        [
            "=COUNTA(Startups!A2:A)",
            "=COUNTA(Products!A2:A)",
            "=COUNTA(Research_Papers!A2:A)",
            "=COUNTA(AI_News!A2:A)",
            "=COUNTA(AI_Jobs!A2:A)",
            '=COUNTIF(Research_Papers!T2:T, "TRUE") + COUNTIF(AI_News!R2:R, "TRUE") + COUNTIF(AI_Jobs!AH2:AH, "TRUE") + COUNTIF(Startups!V2:V, "TRUE") + COUNTIF(Products!X2:X, "TRUE")',
            '=COUNTIF(AI_News!S2:S, "TRUE") + COUNTIF(AI_Jobs!AI2:AI, "TRUE") + COUNTIF(Research_Papers!U2:U, "TRUE") + COUNTIF(Startups!W2:W, "TRUE") + COUNTIF(Products!Y2:Y, "TRUE")',
            "=COUNTA(GitHub_Repositories!A2:A)",
            "=COUNTA(GitHub_Metrics!A2:A)",
            "=COUNTA(Collection_Logs!A2:A)"
        ],
        # Row 6: Blank
        ["", "", "", "", "", "", "", ""],
        # Row 7: Section Header for Data Tables
        ["ECOSYSTEM ANALYTICS & DISTRIBUTION SUMMARY TABLES", "", "", "", "", "", "", ""],
        # Row 8: Table Header 1 (Jobs by Taxonomy) and Table Header 2 (Startups by Focus Area)
        ["Job Taxonomy Category", "Vacancy Count", "", "Startup Focus Area", "Company Count", "", "Vacancy Lifecycle Status", "Job Count"],
        # Rows 9+: Live Dynamic Aggregation Queries
        [
            '=IFERROR(QUERY(AI_Jobs!E2:E, "SELECT E, COUNT(E) WHERE E IS NOT NULL GROUP BY E ORDER BY COUNT(E) DESC LABEL E \'\', COUNT(E) \'\'", 0), "")',
            "", "",
            '=IFERROR(QUERY(Startups!C2:C, "SELECT C, COUNT(C) WHERE C IS NOT NULL GROUP BY C ORDER BY COUNT(C) DESC LABEL C \'\', COUNT(C) \'\'", 0), "")',
            "", "",
            '=IFERROR(QUERY(AI_Jobs!W2:W, "SELECT W, COUNT(W) WHERE W IS NOT NULL GROUP BY W ORDER BY COUNT(W) DESC LABEL W \'\', COUNT(W) \'\'", 0), "")',
            ""
        ]
    ]

    execute_with_backoff(lambda: service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Dashboard!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values_data}
    ).execute())

    # 2. Add Additional Aggregation Tables for Charts (in Columns J to R)
    side_tables = [
        ["Research Paper Categories", "Paper Count", "", "Product Task Categories", "Product Count", "", "News Category", "Article Count"],
        [
            '=IFERROR(QUERY(Research_Papers!E2:E, "SELECT E, COUNT(E) WHERE E IS NOT NULL GROUP BY E ORDER BY COUNT(E) DESC LIMIT 10 LABEL E \'\', COUNT(E) \'\'", 0), "")',
            "", "",
            '=IFERROR(QUERY(Products!D2:D, "SELECT D, COUNT(D) WHERE D IS NOT NULL GROUP BY D ORDER BY COUNT(D) DESC LIMIT 10 LABEL D \'\', COUNT(D) \'\'", 0), "")',
            "", "",
            '=IFERROR(QUERY(AI_News!I2:I, "SELECT I, COUNT(I) WHERE I IS NOT NULL GROUP BY I ORDER BY COUNT(I) DESC LABEL I \'\', COUNT(I) \'\'", 0), "")',
            ""
        ]
    ]

    execute_with_backoff(lambda: service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Dashboard!J8",
        valueInputOption="USER_ENTERED",
        body={"values": side_tables}
    ).execute())

    # 3. Formatting & Visual Styling Requests
    formatting_requests = [
        # Title Banner: Dark Navy #1B365D, White Bold 16pt Text
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 12
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.106, "green": 0.212, "blue": 0.365},
                        "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 14, "bold": True},
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        },
        # Subtitle: Dark Navy #2C4D75, White 10pt Text
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 12
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.173, "green": 0.302, "blue": 0.459},
                        "textFormat": {"foregroundColor": {"red": 0.9, "green": 0.9, "blue": 0.95}, "fontSize": 10, "italic": True},
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        },
        # KPI Card Headers: Light Navy #2C4D75, Bold White 9pt Text
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 3,
                    "endRowIndex": 4,
                    "startColumnIndex": 0,
                    "endColumnIndex": 10
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.106, "green": 0.212, "blue": 0.365},
                        "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 9, "bold": True},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)"
            }
        },
        # KPI Card Values: Pale Ice Blue #EBF3FA, Navy Bold 18pt Text
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 4,
                    "endRowIndex": 5,
                    "startColumnIndex": 0,
                    "endColumnIndex": 10
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.92, "green": 0.95, "blue": 0.98},
                        "textFormat": {"foregroundColor": {"red": 0.106, "green": 0.212, "blue": 0.365}, "fontSize": 16, "bold": True},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,numberFormat)"
            }
        },
        # Section Header: Row 7
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 6,
                    "endRowIndex": 7,
                    "startColumnIndex": 0,
                    "endColumnIndex": 18
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.20, "green": 0.35, "blue": 0.55},
                        "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 11, "bold": True},
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        },
        # Summary Table Headers: Row 8
        {
            "repeatCell": {
                "range": {
                    "sheetId": dashboard_sheet_id,
                    "startRowIndex": 7,
                    "endRowIndex": 8,
                    "startColumnIndex": 0,
                    "endColumnIndex": 18
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.88, "green": 0.92, "blue": 0.96},
                        "textFormat": {"foregroundColor": {"red": 0.106, "green": 0.212, "blue": 0.365}, "fontSize": 9, "bold": True},
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        }
    ]

    execute_with_backoff(lambda: service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": formatting_requests}
    ).execute())

    # 4. Create Native Google Charts via batchUpdate
    chart_requests = [
        # Chart 1: Job Taxonomy Distribution (Bar Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "AI Job Vacancies by Taxonomy Category",
                        "basicChart": {
                            "chartType": "BAR",
                            "legendPosition": "NO_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Number of Vacancies"},
                                {"position": "LEFT_AXIS", "title": "Category"}
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 20,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 1
                                            }]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 20,
                                                "startColumnIndex": 1,
                                                "endColumnIndex": 2
                                            }]
                                        }
                                    },
                                    "targetAxis": "BOTTOM_AXIS",
                                    "colorStyle": {"rgbColor": {"red": 0.106, "green": 0.32, "blue": 0.65}}
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 22,
                                "columnIndex": 0
                            },
                            "widthPixels": 550,
                            "heightPixels": 360
                        }
                    }
                }
            }
        },
        # Chart 2: Startup AI Focus Area Distribution (Pie/Donut Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "AI Startup Domain & Focus Area Distribution",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "pieHole": 0.4,
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 18,
                                        "startColumnIndex": 3,
                                        "endColumnIndex": 4
                                    }]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 18,
                                        "startColumnIndex": 4,
                                        "endColumnIndex": 5
                                    }]
                                }
                            }
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 22,
                                "columnIndex": 6
                            },
                            "widthPixels": 550,
                            "heightPixels": 360
                        }
                    }
                }
            }
        },
        # Chart 3: Vacancy Lifecycle Distribution (Pie Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Vacancy Verification & Lifecycle Status Distribution",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "pieHole": 0.3,
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 12,
                                        "startColumnIndex": 6,
                                        "endColumnIndex": 7
                                    }]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 12,
                                        "startColumnIndex": 7,
                                        "endColumnIndex": 8
                                    }]
                                }
                            }
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 22,
                                "columnIndex": 12
                            },
                            "widthPixels": 500,
                            "heightPixels": 360
                        }
                    }
                }
            }
        },
        # Chart 4: Research Paper Categories (Column Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Research Paper Domain Category Distribution",
                        "basicChart": {
                            "chartType": "COLUMN",
                            "legendPosition": "NO_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Scientific Category"},
                                {"position": "LEFT_AXIS", "title": "Paper Count"}
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 18,
                                                "startColumnIndex": 9,
                                                "endColumnIndex": 10
                                            }]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 18,
                                                "startColumnIndex": 10,
                                                "endColumnIndex": 11
                                            }]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                    "colorStyle": {"rgbColor": {"red": 0.15, "green": 0.45, "blue": 0.35}}
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 42,
                                "columnIndex": 0
                            },
                            "widthPixels": 550,
                            "heightPixels": 360
                        }
                    }
                }
            }
        },
        # Chart 5: AI Product Task Categories (Bar Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Commercial AI Product Categories",
                        "basicChart": {
                            "chartType": "BAR",
                            "legendPosition": "NO_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Product Count"},
                                {"position": "LEFT_AXIS", "title": "Task Category"}
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 18,
                                                "startColumnIndex": 12,
                                                "endColumnIndex": 13
                                            }]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{
                                                "sheetId": dashboard_sheet_id,
                                                "startRowIndex": 7,
                                                "endRowIndex": 18,
                                                "startColumnIndex": 13,
                                                "endColumnIndex": 14
                                            }]
                                        }
                                    },
                                    "targetAxis": "BOTTOM_AXIS",
                                    "colorStyle": {"rgbColor": {"red": 0.70, "green": 0.35, "blue": 0.15}}
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 42,
                                "columnIndex": 6
                            },
                            "widthPixels": 550,
                            "heightPixels": 360
                        }
                    }
                }
            }
        },
        # Chart 6: News Category Distribution (Pie Chart)
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "AI News Editorial Category Distribution",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "pieHole": 0.4,
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 15,
                                        "startColumnIndex": 15,
                                        "endColumnIndex": 16
                                    }]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": dashboard_sheet_id,
                                        "startRowIndex": 7,
                                        "endRowIndex": 15,
                                        "startColumnIndex": 16,
                                        "endColumnIndex": 17
                                    }]
                                }
                            }
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": dashboard_sheet_id,
                                "rowIndex": 42,
                                "columnIndex": 12
                            },
                            "widthPixels": 500,
                            "heightPixels": 360
                        }
                    }
                }
            }
        }
    ]

    execute_with_backoff(lambda: service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": chart_requests}
    ).execute())

    return {
        "status": "DASHBOARD_BUILT",
        "kpis_configured": 8,
        "charts_configured": 6,
        "styling": "NAVY_WHITE_EXECUTIVE"
    }
