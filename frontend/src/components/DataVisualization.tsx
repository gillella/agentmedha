import React from 'react';
import Plot from 'react-plotly.js';
import { BarChart3, TrendingUp, PieChart } from 'lucide-react';

interface DataVisualizationProps {
  data: any[];
  visualizationType?: string;
  title?: string;
}

export default function DataVisualization({ data, visualizationType = 'table', title }: DataVisualizationProps) {
  if (!data || data.length === 0) {
    return (
      <div className="p-4 text-gray-500 text-sm">
        No data to visualize
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  // Helper to detect numeric columns
  const isNumericColumn = (key: string) => {
    return data.some(row => typeof row[key] === 'number' || !isNaN(parseFloat(row[key])));
  };

  // Helper to get column values
  const getColumnValues = (key: string) => {
    return data.map(row => {
      const val = row[key];
      return typeof val === 'number' ? val : parseFloat(val) || 0;
    });
  };

  // Bar Chart for aggregations (GROUP BY queries)
  if (visualizationType === 'bar_chart' && columns.length >= 2) {
    const labelColumn = columns[0]; // First column for labels
    const numericColumns = columns.slice(1).filter(isNumericColumn);
    
    if (numericColumns.length > 0) {
      const traces = numericColumns.map((col, idx) => ({
        x: data.map(row => row[labelColumn]),
        y: getColumnValues(col),
        name: col,
        type: 'bar' as const,
        marker: {
          color: [
            '#3b82f6', // blue
            '#10b981', // green
            '#f59e0b', // amber
            '#ef4444', // red
            '#8b5cf6', // purple
            '#ec4899', // pink
          ][idx % 6],
        },
      }));

      return (
        <div className="w-full bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">
              {title || 'Bar Chart Visualization'}
            </h3>
          </div>
          <Plot
            data={traces}
            layout={{
              autosize: true,
              margin: { l: 60, r: 40, t: 40, b: 80 },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { family: 'Inter, system-ui, sans-serif' },
              xaxis: {
                title: labelColumn,
                tickangle: -45,
              },
              yaxis: {
                title: numericColumns[0],
                gridcolor: '#f3f4f6',
              },
              bargap: 0.2,
              hoverlabel: {
                bgcolor: '#1f2937',
                font: { color: 'white' },
              },
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            }}
            style={{ width: '100%', height: '400px' }}
          />
        </div>
      );
    }
  }

  // Line Chart for time series
  if (visualizationType === 'line_chart' && columns.length >= 2) {
    const xColumn = columns[0];
    const numericColumns = columns.slice(1).filter(isNumericColumn);

    if (numericColumns.length > 0) {
      const traces = numericColumns.map((col, idx) => ({
        x: data.map(row => row[xColumn]),
        y: getColumnValues(col),
        name: col,
        type: 'scatter' as const,
        mode: 'lines+markers' as const,
        line: {
          color: [
            '#3b82f6', // blue
            '#10b981', // green
            '#f59e0b', // amber
            '#ef4444', // red
            '#8b5cf6', // purple
          ][idx % 5],
          width: 3,
        },
        marker: { size: 6 },
      }));

      return (
        <div className="w-full bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-gray-900">
              {title || 'Trend Analysis'}
            </h3>
          </div>
          <Plot
            data={traces}
            layout={{
              autosize: true,
              margin: { l: 60, r: 40, t: 40, b: 80 },
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: 'rgba(0,0,0,0)',
              font: { family: 'Inter, system-ui, sans-serif' },
              xaxis: {
                title: xColumn,
                gridcolor: '#f3f4f6',
              },
              yaxis: {
                title: numericColumns[0],
                gridcolor: '#f3f4f6',
              },
              hovermode: 'x unified',
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
            }}
            style={{ width: '100%', height: '400px' }}
          />
        </div>
      );
    }
  }

  // Pie Chart (if single numeric column for parts of a whole)
  if (visualizationType === 'pie_chart' && columns.length === 2 && isNumericColumn(columns[1])) {
    return (
      <div className="w-full bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900">
            {title || 'Distribution'}
          </h3>
        </div>
        <Plot
          data={[{
            values: getColumnValues(columns[1]),
            labels: data.map(row => row[columns[0]]),
            type: 'pie' as const,
            marker: {
              colors: [
                '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 
                '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
              ],
            },
            textinfo: 'label+percent',
            textposition: 'outside',
            automargin: true,
          }]}
          layout={{
            autosize: true,
            margin: { l: 20, r: 20, t: 20, b: 20 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Inter, system-ui, sans-serif' },
            showlegend: true,
            legend: {
              orientation: 'v',
              x: 1.1,
              y: 0.5,
            },
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
          }}
          style={{ width: '100%', height: '400px' }}
        />
      </div>
    );
  }

  // Fallback to table
  return (
    <div className="w-full overflow-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {typeof row[col] === 'number' 
                    ? row[col].toLocaleString() 
                    : String(row[col] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


