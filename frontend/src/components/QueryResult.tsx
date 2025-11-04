import { CheckCircle, Clock, Database } from 'lucide-react'

interface QueryResultProps {
  data: any
}

export default function QueryResult({ data }: QueryResultProps) {
  const { query, data: resultData, columns } = data

  return (
    <div className="space-y-6">
      {/* Query info */}
      <div className="bg-card rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Query Results</h2>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-muted-foreground">
              {query.status === 'success' ? 'Success' : query.status}
            </span>
          </div>
        </div>

        {/* Metadata */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-muted-foreground mb-1">Rows Returned</div>
            <div className="font-medium">{query.row_count || 0}</div>
          </div>
          <div>
            <div className="text-muted-foreground mb-1">Execution Time</div>
            <div className="font-medium flex items-center space-x-1">
              <Clock className="h-3 w-3" />
              <span>{query.execution_time_ms || 0}ms</span>
            </div>
          </div>
          <div>
            <div className="text-muted-foreground mb-1">Cached</div>
            <div className="font-medium">
              {query.is_cached ? 'Yes' : 'No'}
            </div>
          </div>
        </div>

        {/* Generated SQL */}
        {query.generated_sql && (
          <div className="mt-4">
            <div className="text-sm text-muted-foreground mb-2">Generated SQL:</div>
            <pre className="bg-muted p-4 rounded-md overflow-x-auto text-xs">
              <code>{query.generated_sql}</code>
            </pre>
          </div>
        )}
      </div>

      {/* Data table */}
      {resultData && resultData.length > 0 && (
        <div className="bg-card rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Data ({resultData.length} rows)</span>
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  {columns.map((column: string) => (
                    <th
                      key={column}
                      className="text-left py-3 px-4 font-medium text-muted-foreground"
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {resultData.map((row: any, index: number) => (
                  <tr key={index} className="border-b border-border last:border-0">
                    {columns.map((column: string) => (
                      <td key={column} className="py-3 px-4">
                        {row[column] !== null && row[column] !== undefined
                          ? String(row[column])
                          : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Insights (if available) */}
      {query.insights && query.insights.length > 0 && (
        <div className="bg-card rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Insights</h3>
          <ul className="space-y-2">
            {query.insights.map((insight: string, index: number) => (
              <li key={index} className="text-sm text-muted-foreground">
                • {insight}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}














